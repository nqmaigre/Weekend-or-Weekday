import h5py
import numpy as np
from datetime import datetime
import tensorflow as tf
import logging
import os
import random

# disable the warnings
logging.getLogger('tensorflow').disabled = True

# data needed has been created and saved in raw_data.h5 and gen_data.h5

# read the raw data from raw_data.h5
# the raw data is from teacher and the data has been processed by process_data.py
# the raw data is of 138 days
raw_h5f = h5py.File('raw_data.h5', 'r')
datas = raw_h5f['datas'][:] # an array which has 138 elements
# print(datas.shape) 
# the shape of datas is (138, 32, 32, 96) 
# 32*32 refers to the 32*32 grids
# 96 = 48*2, 48 means that every day has 48 slots
# 2 means that for every slot, inflow, outflow are taken into account
others = raw_h5f['others'][:] # an array which has 138 elements
# print(others.shape) 
# the shape of others is (138, 19)
# 19 refers to other information such as weather and windspeed 
labels = raw_h5f['labels'][:] # an array which has 138 elements
# print(labels.shape) 
# the shape of labels is (138, 2)
# [1, 0] means weekend and [0, 1] weekday
raw_h5f.close()
print('read raw data ok')

# read the generated data from gen_data.h5 
# the data was generated in the way of Data Augmentation
# Data Augmentation helps to avoid overfitting
gen_h5f = h5py.File('gen_data.h5', 'r')
gen_d = gen_h5f['datas'][:]
# print(gen_d.shape)
# the shape of gen_d is (828, 32, 32, 96)
gen_o = gen_h5f['others'][:]
# print(gen_o.shape)
# the shape of gen_d is (828, 19)
gen_l = gen_h5f['labels'][:]
# print(gen_l.shape)
# the shape of gen_l is (828, 2)
gen_h5f.close()
print('read gen data ok')

# 打乱顺序
num_example = datas.shape[0]
arr = np.arange(num_example)
np.random.shuffle(arr)
datas = datas[arr]
others = others[arr]
labels = labels[arr]

# 将所有数据分为训练集和验证集
ratio = 0.8
train_size = np.int(num_example*ratio)
x_train = datas[:train_size]
y_train = labels[:train_size]
o_train = others[:train_size]
x_test = datas[train_size:]
y_test = labels[train_size:]
o_test = others[train_size:]

# following are some functions used in making the neural network
# use CNN to extract the information from datas/gen_d (namely the information from inflows and outflows)
# use normal NN to extract the information from others/gen_o
# then combine the information extracted by CNN and the information extracted from others/gen_o, and use following neural network to do classification work
def weight_variable(shape):
	initial = tf.truncated_normal(shape, stddev=0.1)
	return tf.Variable(initial)

def bias_variable(shape):
	initial = tf.constant(0.1, shape=shape)
	return tf.Variable(initial)

def conv2d(x, W):
	return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool_2x2(x):
	return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                    	strides=[1, 2, 2, 1], padding='SAME')

def max_pool_4x4(x):
	return tf.nn.max_pool(x, ksize=[1, 4, 4, 1],
                    	strides=[1, 4, 4, 1], padding='SAME')

datas_placeholder = tf.placeholder(tf.float32, [None, 32, 32, 48*2]) # use datas/gen_d as input
other_placeholder = tf.placeholder(tf.float32, [None, 19]) # use others/gen_o as input
labels_placeholder = tf.placeholder(tf.float32, [None, 2]) # use labels/gen_l as input
dropout_placeholder = tf.placeholder(tf.float32)

# num_conv1 = 16 # 第二层卷积核数量
# num_conv2 = 32 # 第二层卷积核数量
# num_fc = 128 # inflow outflow 特征提取数量
# num_other = 19 # 其他信息的特征数量
# num_o_fc1 = 128 # 其他信息中提取出的特振数量
# num_fc2 = 128 # 所有特征提取出的特征数量

num_conv1 = 16 # the amount of convolution kernels of layer1
num_conv2 = 32 # the amount of convolution kernels of layer2
num_fc = 128 # the amount of features extraced by CNN
num_other = 19 # the dimensions of others/gen_o
num_o_fc1 = 128 # the amount of features extraced by normal NN
num_fc2 = 64 # the amount of features extraced by the total network

# convulutional layer1
W_conv1 = weight_variable([5, 5, 48*2, num_conv1])
b_conv1 = bias_variable([num_conv1])
h_conv1 = tf.nn.relu(conv2d(datas_placeholder, W_conv1) + b_conv1)
h_pool1 = max_pool_2x2(h_conv1)

# convulutional layer2
W_conv2 = weight_variable([5, 5, num_conv1, num_conv2])
b_conv2 = bias_variable([num_conv2])
h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
h_pool2 = max_pool_2x2(h_conv2)

b_fc1 = bias_variable([num_fc])
h_pool2_flat = tf.reshape(h_pool2, [-1, 8*8*num_conv2])
W_fc1 = weight_variable([8*8*num_conv2, num_fc])
h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)
h_fc1_drop = tf.nn.dropout(h_fc1, dropout_placeholder) # use dropout to avoid overfitting

W_o_fc1 = weight_variable([num_other, num_o_fc1])
b_o_fc1 = bias_variable([num_o_fc1])
h_o_fc1 = tf.nn.relu(tf.matmul(other_placeholder, W_o_fc1) + b_o_fc1)
h_o_fc1_drop = tf.nn.dropout(h_o_fc1, dropout_placeholder) # use dropout to avoid overfitting

# concatenate the features extracted from CNN and normal NN
h_concat = tf.concat([h_fc1_drop, h_o_fc1_drop], axis=1) #tf.reshape(tf.concat(1, [h_fc1, other_placeholder]), [-1, num_fc+19])

W_fc2 = weight_variable([num_fc+num_o_fc1, num_fc2])
b_fc2 = bias_variable([num_fc2])
h_fc2 = tf.nn.relu(tf.matmul(h_concat, W_fc2) + b_fc2)
h_fc2_drop = tf.nn.dropout(h_fc2, dropout_placeholder) # use dropout to avoid overfitting

W_fc3 = weight_variable([num_fc2, 2])
b_fc3 = bias_variable([2])
y_conv = tf.nn.softmax(tf.matmul(h_fc2_drop, W_fc3) + b_fc3)

# add L2 regularization to avoid overfitting
tf.add_to_collection(tf.GraphKeys.WEIGHTS, W_conv1)
tf.add_to_collection(tf.GraphKeys.WEIGHTS, W_conv2)
tf.add_to_collection(tf.GraphKeys.WEIGHTS, W_fc1)
tf.add_to_collection(tf.GraphKeys.WEIGHTS, W_o_fc1)
tf.add_to_collection(tf.GraphKeys.WEIGHTS, W_fc2)
tf.add_to_collection(tf.GraphKeys.WEIGHTS, W_fc3)
regularizer = tf.contrib.layers.l2_regularizer(scale=10.0/x_test.shape[0])
reg_term = tf.contrib.layers.apply_regularization(regularizer)

cross_entropy = -tf.reduce_sum(labels_placeholder*tf.log(y_conv))
loss = cross_entropy + reg_term # loss function

train_step = tf.train.AdamOptimizer(1e-4).minimize(loss)
correct_prediction = tf.equal(tf.argmax(y_conv,1), tf.argmax(labels_placeholder,1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))

sess = tf.InteractiveSession()
sess.run(tf.initialize_all_variables())

saver = tf.train.Saver()

# train the model
for i in range(10000):
	rand_index = np.random.choice(x_train.shape[0], size = 32)
	rand_x = x_train[rand_index]
	rand_y = y_train[rand_index]
	rand_o = o_train[rand_index]
	if i % 100 == 0:
		train_feed_dict = {
			datas_placeholder: rand_x, 
			labels_placeholder: rand_y, 
			other_placeholder: rand_o,
			dropout_placeholder: 1.0
		}
		test_feed_dict = {
			datas_placeholder: x_test, 
			labels_placeholder: y_test, 
			other_placeholder: o_test,
			dropout_placeholder: 1.0
		}
		train_accuracy = accuracy.eval(train_feed_dict)
		test_accuracy = accuracy.eval(test_feed_dict)
		train_loss = cross_entropy.eval(train_feed_dict)
		print("step %d, accuracy %g, test_accuracy %g, loss %g"%(i, train_accuracy, test_accuracy, train_loss))

	if (i+1) % 1000 == 0:
		saver.save(sess, './checkpoint/MyModel', global_step=(i+1))

	train_step.run(feed_dict={
		datas_placeholder: rand_x, 
		labels_placeholder: rand_y, 
		other_placeholder: rand_o,
		dropout_placeholder: 0.5
	})

print('train ends')


# use raw data to test the model
test_feed_dict = {
	datas_placeholder: x_test, 
	labels_placeholder: y_test, 
	other_placeholder: o_test,
	dropout_placeholder: 1.0
}
test_accuracy = accuracy.eval(test_feed_dict)
test_loss = cross_entropy.eval(test_feed_dict)

print("accuracy on test data %g, loss on test data %g"%(test_accuracy, test_loss))
# now the classification work finished, and got 100% accuracy