# from typing import Any, Dict, Optional, Protocol, Type, Union

# from pydantic import BaseModel


# class DatalogueProtocol(Protocol):
#     def convey(
#         self,
#         model: BaseModel,
#         schema: Type[BaseModel],
#         prompt: Optional[str] = None,
#         config: Optional[Dict[str, Union[str, Any]]] = None,
#     ) -> BaseModel:
#         """
#         Validate and transform data based on a schema using Pydantic.

#         Args:
#         - model: The Pydantic model that represents the expected structure.
#         - schema: The schema to which the model data should adhere.
#         - prompt: An optional prompt guiding the transformation.
#         - config: Optional configurations guiding the transformation process.

#         Returns:
#         - A validated and transformed Pydantic model instance.
#         """
#         ...

#     async def convey_async(
#         self,
#         model: BaseModel,
#         schema: Type[BaseModel],
#         prompt: Optional[str] = None,
#         config: Optional[Dict[str, Union[str, Any]]] = None,
#     ) -> BaseModel:
#         ...


# import json
# import logging
# import os
# from typing import Type, Union

# from httpx import AsyncClient
# from pydantic import BaseModel, Field, HttpUrl

# API_URL: HttpUrl = HttpUrl("https://api.openai.com/v1/chat/completions")
# CLIENT = AsyncClient()

# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)
# # logger.setLevel(logging.INFO)


# def delkey(d: dict, k: Union[str, int, float, bool, None]) -> None:
#     """Recursively removes a key from a dictionary and all its nested dictionaries."""
#     if isinstance(d, dict):
#         for key in list(d.keys()):
#             if key == k:
#                 del d[key]
#             else:
#                 delkey(d[key], k)


# def schema_to_function(schema: Type[BaseModel]):
#     assert schema.__doc__, f"{schema.__name__} must have a docstring."
#     assert (
#         "title" not in schema.model_fields.keys()
#     ), "`title` is a reserved keyword and cannot be used as a field name."
#     schema_dict = schema.model_json_schema()
#     delkey(schema_dict, "title")

#     return {
#         "name": schema.__name__,
#         "description": schema.__doc__,
#         "parameters": schema_dict,
#     }


# async def gpt4(
#     data: BaseModel, output_model: Type[BaseModel], system_prompt: str | None = None
# ):
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
#     }
#     user_message = {
#         "role": "function",
#         "content": data.model_dump_json(),
#         "name": data.__class__.__name__,
#     }
#     messages = [{"role": "system", "content": system_prompt}] if system_prompt else []
#     messages.append(user_message)
#     json_data = {
#         "model": "gpt-4-0613",
#         "messages": messages,
#         "stream": False,
#         "functions": [
#             schema_to_function(data.__class__),
#             schema_to_function(output_model),
#         ],
#         "function_call": {"name": output_model.__name__},
#         "temperature": 0.0,
#     }
#     r = await CLIENT.post(
#         str(API_URL),
#         json=json_data,
#         headers=headers,
#         timeout=None,
#     )
#     logger.debug(f"Response: {r}")
#     rj = r.json()
#     logger.debug(f"Response JSON: {rj}")
#     content = rj["choices"][0]["message"]["function_call"]["arguments"]
#     content = json.loads(content)
#     return output_model.model_validate(content)


# class OpenAIDatalogue(DatalogueProtocol):
#     async def convey_async(
#         self,
#         model: BaseModel,
#         schema: Dict[str, Any],
#         prompt: Optional[str] = None,
#         config: Optional[Dict[str, Union[str, Any]]] = None,
#     ) -> BaseModel:
#         ...

#     def convey(
#         self,
#         model: BaseModel,
#         schema: Dict[str, Any],
#         prompt: Optional[str] = None,
#         config: Optional[Dict[str, Union[str, Any]]] = None,
#     ) -> BaseModel:
#         ...
