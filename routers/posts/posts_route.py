from fastapi import status, Depends, APIRouter
from core.exceptions import  PostServiceException
from db import get_db
from typing import List, Optional
from routers.posts.posting_services import create_comment_service, create_post_service, delete_commentById_service, delete_post_by_id_service, fetch_post_by_id_service, get_Nposts_service, get_post_comments_service, update_post_by_id_service
from utils.ai_responce_handler import handle_service_response
from utils.schemas import PostLikesOutSchema, PostResponseSchema, PostCreateSchema
from Oauth2 import get_user_jwt_payload
from utils.schemas import APIResponse
from sqlalchemy.ext.asyncio import AsyncSession
from utils.schemas import CommentCreateSchema, CommentResponseSchema




router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)





@router.get("/", response_model=List[PostLikesOutSchema])
async def get_all_posts(db: AsyncSession = Depends(get_db), user_payload = Depends(get_user_jwt_payload), limit: int = 10, offset: int = 0, search: Optional[str] = None, personal_only: bool = False) -> List[PostLikesOutSchema]:
    result: APIResponse = await get_Nposts_service(user_payload=user_payload, db=db, limit=limit, search=search, offset=offset, personal_only=personal_only)
    return handle_service_response(result, PostServiceException) #either i get reult of PostServiceException




@router.post("/", response_model=PostResponseSchema) 
async def create_post(new_post: PostCreateSchema,  user_payload = Depends(get_user_jwt_payload), db: AsyncSession = Depends(get_db)) -> PostResponseSchema:
    result: APIResponse = await create_post_service(user_payload=user_payload, db=db, new_post=new_post)
    return handle_service_response(result, PostServiceException)



@router.get("/{id}", response_model=PostLikesOutSchema)  
async def get_post_by_id(id: int, user_payload = Depends(get_user_jwt_payload), db: AsyncSession = Depends(get_db)) -> PostLikesOutSchema:  
    result: APIResponse = await fetch_post_by_id_service(user_payload=user_payload, db=db, id=id)
    return handle_service_response(result, PostServiceException)





@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT) 
async def delete_post_by_id(id: int, user_payload = Depends(get_user_jwt_payload), db: AsyncSession = Depends(get_db)):
    result: APIResponse = await delete_post_by_id_service(user_payload=user_payload, db=db, id=id)
    return handle_service_response(result, PostServiceException)





@router.put("/{id}", response_model=PostResponseSchema)
async def update_by_id(id: int, post_data: PostCreateSchema, user_payload = Depends(get_user_jwt_payload), db: AsyncSession = Depends(get_db)) -> PostResponseSchema:
    result: APIResponse = await update_post_by_id_service(user_payload=user_payload, db=db, id=id, post_data=post_data)
    return handle_service_response(result, PostServiceException)



@router.post("/{post_id}/comments", status_code=status.HTTP_201_CREATED, response_model=CommentResponseSchema)
async def create_comment(post_id: int, comment_data: CommentCreateSchema, user_payload = Depends(get_user_jwt_payload), db: AsyncSession = Depends(get_db)) -> CommentResponseSchema:
    result: APIResponse = await create_comment_service(user_payload=user_payload, post_id=post_id, db=db, comment_data=comment_data)
    return handle_service_response(result, PostServiceException)





@router.get("/{post_id}/comments", response_model=List[CommentResponseSchema])
async def get_comments_for_post(post_id: int, limit: int = 10, offset: int = 0, search: Optional[str] = None, db: AsyncSession = Depends(get_db), user_payload = Depends(get_user_jwt_payload)) -> List[CommentResponseSchema]: 
    result: APIResponse = await get_post_comments_service(user_payload, post_id=post_id, db=db, limit=limit, offset=offset, search=search)
    return handle_service_response(result, PostServiceException)



#the one who left the comments is the one who can delete it!
@router.delete("/{post_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(post_id: int, comment_id: int, user_payload = Depends(get_user_jwt_payload), db: AsyncSession = Depends(get_db)):
    result: APIResponse = await delete_commentById_service(post_id=post_id, db=db, comment_id=comment_id, user_payload=user_payload)
    return handle_service_response(result, PostServiceException)