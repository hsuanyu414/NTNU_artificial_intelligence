from numpy import *
import matplotlib.pyplot as plt
import math
import time


train_in = array([[0, 2, 0], [0, 0, 1], [0, 1, 1], [1, 0, 1], [1, 1, 1]])
train_sol = array([[0, 0, 0, 1, 1]]).T

def epoch_error(epoch, learning_rate):
  random.seed(1)
  nn_weights = 2 * random.random((3, 1)) - 1
  # print(nn_weights)
  x = range (epoch)
  y = []
  y_test = []
  test_in = array([1, 0, 0])
  min_train_loss = 999
  min_test_loss = 999

  start = time.time()
  # print(sum(abs(train_sol-(1/(1+exp(-(dot(train_in, nn_weights)))))))/5)
  for i in range (epoch):
    # print("\n i=", i, "\nnn_weight=\n", nn_weights)
    train_out = 1/(1+exp(-(dot(train_in, nn_weights))))
    test_out = 1/(1+exp(-(dot(test_in, nn_weights))))
    # print("train_out = \n", train_out)
    mae = sum(abs(train_out-train_sol))/5
    min_train_loss = min(min_train_loss, mae)
    e = sum(abs(test_out-1))
    min_test_loss = min(min_test_loss, e)
    y.append(mae)
    y_test.append(e)
    nn_weights += learning_rate*dot(train_in.T, (train_sol-train_out)*train_out*(1-train_out))
  end = time.time()
  plt.plot(x, y, label='Train Loss')
  plt.plot(x, y_test, label='Test Loss')
  plt.legend(loc='upper right')
  plt.show()
  plt.close() 
  print('min train loss:'+str(round(min_train_loss, 4)))
  # print('appear at ' +str(y.index(min_train_loss)+1)+' th time')
  print('min test loss:'+str(round(min_test_loss, 4)))
  # print('appear at ' +str(y_test.index(min_test_loss)+1)+' th time')
  print('it cost '+str(round(end-start, 4))+' sec to execute')

epoch = 200
for i in range (4):
  epoch_error(epoch, 0.1)
  epoch_error(epoch, 1)
  epoch *= 10