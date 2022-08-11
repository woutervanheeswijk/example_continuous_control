# -*- coding: utf-8 -*-
"""
A Continuous Control Implementation for TensorFlow 2.0
Author: W.J.A. van Heeswijk
Date: 11-8-2020
This code is supplemental to the following note:
'Implementing Gaussian Actor Networks for  Continuous Control in TensorFlow 2.0'
https://www.researchgate.net/publication/343714359_Implementing_Gaussian_Actor_Networks_for_Continuous_Control_in_TensorFlow_20
Corresponding blog post:
https://towardsdatascience.com/a-minimal-working-example-for-continuous-policy-gradients-in-tensorflow-2-0-d3413ec38c6b
Python 3.8 and TensorFlow 2.3 were used to write the algorithm
This code has been published under the GNU GPLv3 license
"""

# Needed for training the network
import numpy as np
import tensorflow as tf
import tensorflow.keras as keras
import tensorflow.keras.layers as layers
import tensorflow.keras.initializers as initializers

# Needed for animation
import matplotlib.pyplot as plt

"""Plot output"""
def plot():
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

        # Append arrays
        epoch_ar.append(int(i))
        mu_ar.append(float(mu))
        sigma_ar.append(float(sigma))
        reward_ar.append(float(reward))
        target_ar.append(float(mu_target))
    
        # Plot outcomes
        ax.plot(epoch_ar,mu_ar,label='mu')
        ax.plot(epoch_ar,sigma_ar,label='sigma')
        ax.plot(epoch_ar,reward_ar,label='reward')
        ax.plot(epoch_ar,target_ar,label='target')
    
        # Add labels and legend
        plt.xlabel('Episode')
        plt.ylabel('Parameter value')
        plt.grid()
        plt.legend(loc='best')
        
        plt.show() 

"""Construct the actor network with mu and sigma as output"""
def ConstructActorNetwork(bias_mu, bias_sigma):
    inputs = layers.Input(shape=(1,)) #input dimension
    hidden1 = layers.Dense(5, activation="relu",kernel_initializer=initializers.he_normal())(inputs)
    hidden2 = layers.Dense(5, activation="relu",kernel_initializer=initializers.he_normal())(hidden1)
    mu = layers.Dense(1, activation="linear",kernel_initializer=initializers.Zeros(),\
                         bias_initializer=initializers.Constant(bias_mu))(hidden2) 
    sigma = layers.Dense(1, activation="softplus",kernel_initializer=initializers.Zeros(),\
                         bias_initializer=initializers.Constant(bias_sigma))(hidden2) 

    actor_network = keras.Model(inputs=inputs, outputs=[mu,sigma]) 
    
    
    return actor_network

"""Weighted Gaussian log likelihood loss function"""
def CustomLossGaussian(state, action, reward): 
        # Obtain mu and sigma from actor network
        nn_mu, nn_sigma = actor_network(state)
        
        # Obtain pdf of Gaussian distribution
        pdf_value = tf.exp(-0.5 *((action - nn_mu) / (nn_sigma))**2) *\
            1/(nn_sigma*tf.sqrt(2 *np.pi))

        # Compute log probability
        log_probability = tf.math.log(pdf_value + 1e-5)
        
        # Compute weighted loss
        loss_actor = - reward * log_probability
        
        return loss_actor

"""Main code"""
# Initialize fixed state
state = tf.constant([[1.0]])

# Define properties reward function
mu_target = 4.0
target_range = 0.25
max_reward = 1.0

# Create actor network
bias_mu = 0.0  #bias 0.0 yields mu=0.0 with linear activation function
bias_sigma = 0.55 #bias 0.55 yields sigma=1.0 with softplus activation function
actor_network = ConstructActorNetwork(bias_mu , bias_sigma)
opt = keras.optimizers.Adam(learning_rate=0.001)

# Initialize arrays for plot
epoch_ar = []
mu_ar = []
sigma_ar=[]
reward_ar=[]
target_ar=[]

for i in range(10000 + 1):    
    
    # Obtain mu and sigma from network
    mu, sigma = actor_network(state)
    
    # Draw action from normal distribution
    action = tf.random.normal \
        ([1], mean=mu, stddev=sigma)
   
    # Compute reward
    reward = max_reward/ max(target_range,abs(mu_target-action)) * target_range

    # Update network weights  
    with tf.GradientTape() as tape:   
        # Compute Gaussian loss
        loss_value = CustomLossGaussian(state, action, reward)
        
        # Compute gradients
        grads = tape.gradient(loss_value, actor_network.trainable_variables)
 
        #Apply gradients to update network weights
        opt.apply_gradients(zip(grads, actor_network.trainable_variables))
        
        
    # Update console output and plot
    if np.mod(i, 100) == 0:
           
        print('\n======episode',i, '======')
        print('mu',float(mu))
        print('sigma',float(sigma))
        print('action',float(action))
        print('reward',float(reward))
        print('loss',float(loss_value))
        
        plot() 
