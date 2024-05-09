from core.logging_utils import setup_logger
from fastapi import Request


api_logger = setup_logger("api_analysis_logger")


def logging_dependency(request: Request):
    api_logger.info(f"{request.method} {request.url}")
    api_logger.info("Params:")
    for name, value in request.path_params.items():
        api_logger.info(f"\t{name}: {value}")
    for name, value in request.query_params.items():
        api_logger.info(f"\t{name}: {value}")
    if request.body():
        api_logger.info(request.body())
    api_logger.info("Headers:")
    for name, value in request.headers.items():
        api_logger.info(f"\t{name}: {value}")
    api_logger.info("\n")


# def log_api_call(request: Request, logger=None, log_response: bool = False):
#     """
#     this decorator is used for opening and closing connection to the database
#     """
#
#     def decorator(function):
#         @wraps(function)
#         def connection_handler(*args, **kwargs):
#             if logger:
#                 logger.info("API called from ip address: " + str(request.url) + ", with method: " + str(request.method) +
#                             " with params: " + str(request.path_params))
#             try:
#                 response = function(*args, **kwargs)
#                 if logger and log_response:
#                     logger.info("Response from the API call: " + str(response))
#
#                 return response
#             except:
#                 if logger:
#                     logger.exception("Error in calling the function.")
#
#         return connection_handler
#
#     return decorator
