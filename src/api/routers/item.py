from typing import Annotated
from fastapi import APIRouter, Depends, status
from src.services import ItemService
from src.models import item as item_models, Message
from src.api.dependencies import SessionDep
from uuid import UUID

router = APIRouter(
    prefix="/items",
    tags=["Item Endpoints"],
    responses={
        201: {"description": "Item created successfully"},
        404: {"description": "Item not found"},
    },
)


# annotate dependencies
def get_item_service(session: SessionDep):
    return ItemService(session=session)


ItemServiceDep = Annotated[ItemService, Depends(get_item_service)]


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=item_models.ItemPublicResponse,
)
async def add_one_item(
    data: item_models.ItemCreate,
    item_service: ItemServiceDep,
):
    """
    Create new item record
    """
    item = await item_service.create_item(data)

    return item_models.ItemPublicResponse(
        message="Item created successfully", data=item
    )


@router.get("/", response_model=item_models.ItemsPublicResponse)
async def get_all_items(
    item_service: ItemServiceDep,
    skip: int = 0,
    limit: int = 10,
    query: item_models.ItemSearch = Depends(),
):
    """
    Get all item records
    """
    data = await item_service.get_all_items(skip=skip, limit=limit, query=query)

    return item_models.ItemsPublicResponse(
        **vars(data), message="Items retrieved successfully"
    )


@router.get("/{id}", response_model=item_models.ItemPublicResponse)
async def get_one_item_by_id(id: UUID, item_service: ItemServiceDep):
    """
    Get one item by id
    """
    item = await item_service.get_item_by_id(id=id)

    return item_models.ItemPublicResponse(
        message="Item retrieved successfully", data=item
    )


@router.patch("/{id}", response_model=item_models.ItemPublicResponse)
async def update_one_item_by_id(
    id: UUID,
    data: item_models.ItemUpdate,
    item_service: ItemServiceDep,
):
    """
    Update item record by id
    """
    item = await item_service.update_item_by_id(id, data)

    return item_models.ItemPublicResponse(
        message="Item updated successfully", data=item
    )


@router.delete("/{id}", response_model=Message)
async def delete_one_item_by_id(
    id: UUID,
    item_service: ItemServiceDep,
):
    """
    Deleted item record by id.
    """
    await item_service.delete_item_by_id(id)

    return Message(message="Item deleted successfully")
