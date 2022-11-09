import pickle
from game_objects import *


#
# def save_cfg(cfg, user, data):
#     try:
#         with open(cfg, 'wb') as handle:
#             pickle.dump(user, handle, protocol=pickle.HIGHEST_PROTOCOL)
#             pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
#     except Exception as e:
#         print(f"Function: save_cfg Error-message: {e}")
#
# def load_cfg(cfg):
#     user = User()
#     data = GameInfo()
#     try:
#         with open(cfg, 'rb') as handle:
#             user = pickle.load(handle)
#             data = pickle.load(handle)
#     except Exception as e:
#         print(f"Function: load_cfg Error-message: {e}")
#     finally:
#         data.clear_game_status()
#         return user, data

def save_cfg(cfg, user):
    try:
        with open(cfg, 'wb') as handle:
            pickle.dump(user, handle, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        print(f"Function: save_cfg Error-message: {e}")

def load_cfg(cfg):
    user = User()
    try:
        with open(cfg, 'rb') as handle:
            user = pickle.load(handle)
    except Exception as e:
        print(f"Function: load_cfg Error-message: {e}")
    finally:
        return user