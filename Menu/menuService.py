from Middleware.message import Message


def setReady(peer):
    ready_msg = Message(
        id=str(peer.id),
        type="Ready",
        data={}
    )