from flask import jsonify
def make_error(status_code:int, message:str, action:str)->dict:
    msg_return = dict(
        status = status_code,
        message = message,
        action = action
    )
    response = jsonify(msg_return)
    response.status_code=status_code
    return response