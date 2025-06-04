# Importing built-in modules
import random
from collections import deque

# Importing installed modules
import torch
import numpy as np

# Imporing other modules
from game import GameAI
from model import Linear_QNet, QTrainer


MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


class Agent:

    def __init__(self):
        self.n_games = 1
        self.epsilon = 0  # randomness
        self.gamma = 0.9  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
        self.model = Linear_QNet(20, [256, 256], 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        self.loss = None

    def get_state(self, game):
        state = [
            int(
                not game.no_tile_right and not game.player.collisions["down"]
            ),  # no tile right
            int(
                not game.no_tile_left and not game.player.collisions["down"]
            ),  # no tile left
            int(bool(game.spike_warning_right)),  # spike right
            int(bool(game.spike_warning_left)),  # spike left
            int(
                game.player.rect().move(20, 0).colliderect(game.escape_point)
            ),  # escape point right
            int(
                game.player.rect().move(-20, 0).colliderect(game.escape_point)
            ),  # escape point left
            int(game.movement[1] - game.movement[0] > 0),  # direction right
            int(game.movement[1] - game.movement[0] < 0),  # direction left
            int(
                bool(game.movement[1] - game.movement[0] == 0 and game.player.jumps)
            ),  # player standing
            int(not game.player.jumps),  # player jumps
            int(game.player.collisions["left"]),  # collision left
            int(game.player.collisions["right"]),  # collision right
            int(game.player.collisions["up"]),  # collision up
            int(game.player.collisions["down"]),  # collision down
            game.level,  # map level
            game.player.velocity[0],  # x velocity
            game.player.velocity[1],  # y velocity
            game.countdown,  # time
            game.player.pos[1],  # y position
            game.distance,  # distance between agent and escape point
        ]
        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append(
            (state, action, reward, next_state, done)
        )  # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.loss = self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        final_move = [0, 0, 0]
        self.epsilon = 80 - self.n_games
        if random.randint(0, 200) < self.epsilon:
            final_move[random.randint(0, 2)] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        return final_move


def train():
    record = 0
    print_flag = True
    agent = Agent()
    game = GameAI()
    loss_list = []
    while True:
        if game.dead > 1 or game.completed:
            game.play_step()
        else:
            # get old state
            state_old = agent.get_state(game)

            # get move
            final_move = agent.get_action(state_old)

            # perform move and get new state
            reward, score, done = game.play_step(action=final_move)
            state_new = agent.get_state(game)

            # train short memory
            agent.train_short_memory(state_old, final_move, reward, state_new, done)

            # remember
            agent.remember(state_old, final_move, reward, state_new, done)

            if done:
                agent.n_games += 1
                agent.train_long_memory()
                print_flag = True
                print("Average loss:", sum(loss_list) / len(loss_list))
                loss_list = []

            if score > record:
                record = score
                agent.model.save()
                print("Game", agent.n_games, "Score", score, "Record:", record)
                print("Average loss:", sum(loss_list) / len(loss_list))
                loss_list = []

            if agent.n_games % 100 == 0 and agent.n_games > 0 and print_flag:
                print("Echops:", agent.n_games)
                print_flag = False

            loss_list.append(agent.loss.item())


if __name__ == "__main__":
    train()
