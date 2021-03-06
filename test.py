import torch
import torch.nn as nn 
import torch.nn.functional as F
import torch.multiprocessing as mp
import pickle
from torch.distributions import Categorical
from collections import deque
from os import path

import matplotlib.pyplot as plt

from src.agent import Reward,SkipEnv, gym_env
from src.model import A3C
from src.optimizer import Adam_global
from src.params import *
from src.utils import *

def test_global(idx):
    torch.manual_seed(123+idx)
    env,num_state,num_action = gym_env(world,stage,version,actions)
    model = A3C(num_state,num_action)
    model.load_state_dict(torch.load(path.join(path.dirname(path.abspath(__file__)),'trained_model.pth'),map_location='cpu'))
    model.eval()
    state = torch.from_numpy(env.reset())
    done = True
    step_counter = 0
    total_reward = 0
    acts = deque(maxlen = max_actions)

    while True:
        step_counter += 1

        with torch.no_grad():
            if done:
                hx = torch.zeros((1,512),dtype=torch.float)
                cx = torch.zeros((1,512),dtype=torch.float)
            else:
                hx = hx.detach()
                cx = cx.detach()
        
            action,value,hx,cx = model(state,hx,cx)
            prob = F.softmax(action,dim=-1)
            action = prob.max(1,keepdim=True)[1].numpy()
            state,reward,done,info = env.step(int(action))
            state = torch.from_numpy(state)
            env.render()
            acts.append(action)
            total_reward += reward

        if done:
            break


def dummy_test(idx):
    torch.manual_seed(123+idx)
    env,num_state,num_action = gym_env(world,stage,version,actions)
    
    done = True
    with open('record_reward_average.txt','rb') as fp:
        reward = pickle.load(fp)

    with open('record_acts.txt','rb') as fp:
        acts = pickle.load(fp)

    max_id = reward.index(max(reward))
    acts_8 = acts[max_id]
    print(max(reward))
    print(max_id)

    

    for act in acts_8:
        if done:
            state = env.reset()
        state, reward, done, info = env.step(act)
        env.render()
    
    plt.plot(range(1,len(reward)+1), reward)
    plt.xlabel('Episode')
    plt.ylabel('Episode Rewards Achieved')
    plt.title('Episode Rewards')
    plt.show()
    plt.close()


if __name__ == "__main__":
    torch.manual_seed(123)
    test_global(0)