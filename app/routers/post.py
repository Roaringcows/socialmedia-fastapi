from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func #gives acess to sql func like count
from .. import models, schemas, oauth2
from ..database import get_db


router = APIRouter(
    prefix="/posts",     #has preset path that gets appended by path
    tags=['Posts']      #seperates different paths into groups
)


@router.get("/", response_model=List[schemas.PostOut])      #getting all posts
def get_posts(db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ''):
    # cursor.execute("""SELECT * FROM posts """)        // RAW SQL
    # posts = cursor.fetchall()

    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()      //      query

    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post) #create posts
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):   #stores value in post as a pydantic value; func.get_current_user forces users to be log in to create any post
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, 
    #                 (post.title, post.content, post.published))
    # new_post = cursor.fetchone()

    # conn.commit() #saves the changes to database

    new_post = models.Post(owner_id=current_user.id, **post.dict())       #owner id not in schema must be inputted         #EFFICENT SMARTER CODE  **post.dict() creates an object of the schema and unpacks it for you // RATHER THAN title=post.title, content=post.content, published=post.published     
    db.add(new_post)        #creates new post in SQL ALCHEMY
    db.commit()             #commits
    db.refresh(new_post)    #retrieves the new post and restores it in var new_post

    return new_post


@router.get("/{id}", response_model=schemas.PostOut)     #getting individual posts
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):      #validates that it is indeed a #
    # cursor.execute("""SELECT * from posts WHERE id = %s """, (str(id))) #,
    # post = cursor.fetchone()
    # post = db.query(models.Post).filter(models.Post.id == id).first()       #.first() to get the first query that matches rather than .all() that would keep searching when we know theres just one data

    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    # cursor.execute(
    #     """DELETE FROM posts WHERE id = %s RETURNING *""", (str(id)))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id {id} does not exist")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not authorized to perform requested action")

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)     #update post
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    # cursor.execute("""UPDATE posts SET  title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", 
    #                (post.title, post.content, post.published, str(id)))
    
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id {id} does not exist")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not authorized to perform requested action")

    post_query.update(updated_post.dict(), synchronize_session=False)
    
    db.commit()

    return post_query.first()