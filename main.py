from Game.game import Pong
from Menu.menu import menu

if __name__ == "__main__":
    # Menu
    peer = menu()
    print(f'Peer ID: {peer.id}, IS LEADER: {peer.is_leader}, LEADER ID: {peer.leader_id}')
    '''
    The output of the menu is a Peer object, connected to a set of other peers. 
    Allowing it to send and receive messages. With one, and only one, of the peers being the leader.
    '''

    # Game
    game = Pong(peer)
    game.run()
    game.quit()