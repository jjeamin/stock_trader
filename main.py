import tensorflow as tf
import argparse
import matplotlib.pyplot as plt
from tqdm import tqdm
from lib.env import Kospi200_Env
from lib.utils import get_data, download
from lib.agent.PG import PG


def main(args):
    # get utils
    datas, changes, labels = get_data(args.path)
    num_company, period, num_feature = datas.shape
    # parameter
    input_shape = (num_company, args.window_size, num_feature)
    optimizer = tf.keras.optimizers.Adam()
    loss = 'binary_crossentropy'
    # agent
    agent = PG(input_shape, optimizer, loss)
    agent.summary()
    # env
    env = Kospi200_Env(datas, changes, labels, window_size=args.window_size)

    total_reward_log = []

    # train
    for e in tqdm(range(args.num_episode), total=args.num_episode):
        state = env.reset()

        total_reward = 0
        total_loss = 0

        while True:
            action = agent.get_action(state)
            next_state, reward, done = env.step(action)

            agent.memorize(state, reward)

            env.render(mode='confusion')
            loss = agent.learn()
            total_loss += loss

            if done:
                break

            total_reward += reward
            state = next_state

        total_reward_log.append(sum(total_reward))

        print(f"\n + EPISODE: [{args.num_episode} / {e}] \n"
              f"   + REWARD : {sum(total_reward)} \n"
              f"   + LOSS   : {total_loss}")

    plt.plot(total_reward_log)
    plt.show()


if __name__ == "__main__":
    # parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_episode', type=int, default=1000)
    parser.add_argument('--window_size', type=int, default=10)
    parser.add_argument('--path', type=str, default="./data")
    parser.add_argument('--download', action='store_true')
    args = parser.parse_args()

    if args.download:
        print("Data Download...")
        download(args.path)
    else:
        print("Market Start")
        main(args)
