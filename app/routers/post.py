from fastapi import FastAPI, Response, HTTPException, Depends, APIRouter, status
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy import func, asc

from fastapi_limiter.depends import RateLimiter

router = APIRouter(
    prefix='/posts',
    tags=['Post']
)

@router.get('/', response_model=List[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # cursor.execute("""
    #    SELECT *
    #    FROM posts
    # """)
    # posts = cursor.fetchall()

    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all() --> The unjoined version

    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter = True).group_by(models.Post.id).filter(
        models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    return posts

@router.get('/main', response_model=List[schemas.PostResponse])
def get_all_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # cursor.execute("""
    #    SELECT *
    #    FROM posts
    # """)
    # posts = cursor.fetchall()

    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all() --> The unjoined version

    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter = True).group_by(models.Post.id).filter(models.Post.parent_id == None).filter(
        models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    return posts

@router.get('/profile',  response_model=List[schemas.PostResponse])
def get_profile_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter = True).group_by(models.Post.id).filter(
        models.Post.user_id == current_user.id).all()

    return posts

@router.get('/profile/{id}',  response_model=List[schemas.PostResponse])
def get_profile_posts(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter = True).group_by(models.Post.id).filter(
        models.Post.user_id == id).all()

    return posts

@router.get('/votes/{id}', response_model=schemas.PostVotesResponse)
def get_post_votes(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == id, models.Vote.user_id == current_user.id)
    vote = vote_query.first()

    found_vote = False

    if vote:
        found_vote = True

    return {'found_vote': found_vote}


@router.post('/', status_code=201, response_model=schemas.PostResponseBase)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)): # Store all data in body as python dictionary named payLoad
    # cursor.execute("""
    #    INSERT INTO posts (title, content, published) VALUES(%s, %s, %s) 
    #    RETURNING * 
    # """, (post.title, post.content, post.published)) # %s Represents variable
    
    # new_post = cursor.fetchone()
    # conn.commit()'

    new_post = models.Post(
        user_id = current_user.id, **post.dict()
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@router.get('/{id}', response_model=schemas.PostResponse) 
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)): # automatically convert to integer if possible
    # cursor.execute("""
    #    SELECT * 
    #    FROM posts
    #    WHERE posts.id = %s
    # """, (id,))

    # one_post = cursor.fetchone()

    # post = db.query(models.Post).filter(models.Post.id == id).first() --> The unjoined version

    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter = True).group_by(models.Post.id).filter(
        models.Post.id == id).first()

    if post is None:
        raise HTTPException(status_code=404, detail=f'post with id: {id} was not found')
    return post

@router.delete('/{id}', status_code=204)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""
    #    DELETE
    #    FROM posts
    #    WHERE posts.id = %s
    #    RETURNING *
    # """, (id,))

    # deleted_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=404, 
                            detail=f"post with id: {id} does not exist")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform requested action")

    post_query.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=204)

@router.put('/{id}', response_model=schemas.PostResponseBase)
def update_post(id: int, updated_post: schemas.PostUpdate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""
    #    UPDATE posts
    #    SET title = %s, content = %s, published = %s
    #    WHERE id = %s
    #    RETURNING *
    # """, (post.title, post.content, post.published, id))

    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=404,
                            detail=f'post with id: {id} does not exist')
    
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform requested action")
    
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    
    return post_query.first()

@router.post('/{id}', status_code=201, response_model=schemas.PostResponseBase, dependencies=[Depends(RateLimiter(times=60, seconds=3600))])
def create_post_in_thread(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)): # Store all data in body as python dictionary named payLoad
    # cursor.execute("""
    #    INSERT INTO posts (title, content, published) VALUES(%s, %s, %s) 
    #    RETURNING * 
    # """, (post.title, post.content, post.published)) # %s Represents variable
    
    # new_post = cursor.fetchone()
    # conn.commit()'

    new_post = models.Post(
        parent_id = id,
        user_id = current_user.id, 
        **post.dict()
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@router.get('/threads/{id}', status_code=201, response_model=List[schemas.PostResponse], dependencies=[Depends(RateLimiter(times=240, seconds=3600))])
def get_post_threads(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter = True).group_by(models.Post.id).filter(models.Post.parent_id == id).order_by(asc(models.Post.created_at)).filter(
        models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    return posts
