import paho.mqtt.client as client
from time import sleep
import json
import sys
import random
import os

the_control_flag = 0

server_address = "127.0.0.1"
mqtt_client = client.Client("sonar")
data_directory = r"/home/asim/Desktop/Takshshila/IOT/TestScripts/DATASETS_CLASSIFICATION/BINARY_PROBLEMS"
data_directory_2 = r"/home/asim/Desktop/Takshshila/IOT/TestScripts/DATASETS_CLASSIFICATION"


def prepare_data(data_dir, dataset, seed, short, sep):
    # train_data_file = open('ECG-Train.csv')
    file_path = os.path.join(data_dir, dataset, short + 'Train' + str(seed) + 'N_mod.txt')
    train_data_file = open(file_path)
    train_data = []

    for each_line in train_data_file:
        each_line = each_line.strip().split(sep)
        train_data.append(each_line)

    # test_data_file = open('ECG-Test.csv')
    test_data_file = open(os.path.join(data_dir, dataset, short + 'Test' + str(seed) + 'N_mod.txt'))
    test_data = []

    for each_line in test_data_file:
        each_line = each_line.strip().split(sep)
        test_data.append(each_line)

    list_of_feature_names = []
    for i in range(len(train_data[0])):
        list_of_feature_names.append(train_data[0][i])
    return train_data[1:], test_data[1:], list_of_feature_names


def prepare_data_mc(data_dir, dataset, seed, short, sep):
    print(dataset, seed)
    remove_split = "_".join(dataset.split("_")[:-1])
    file_path = os.path.join(data_dir, dataset, remove_split + '_train' + str(seed) + '_mod.csv')
    train_data_file = open(file_path)
    train_data = []

    for each_line in train_data_file:
        each_line = each_line.strip().split(sep)
        train_data.append(each_line)

    file_path = os.path.join(data_dir, dataset, remove_split + '_test' + str(seed) + '_mod.csv')
    test_data_file = open(file_path)
    test_data = []

    for each_line in test_data_file:
        each_line = each_line.strip().split(sep)
        test_data.append(each_line)

    list_of_feature_names = []
    for i in range(len(train_data[0])):
        list_of_feature_names.append(train_data[0][i])

    #print(train_data[1:], test_data[1:], list_of_feature_names)
    return train_data[1:], test_data[1:], list_of_feature_names


def shuffle_the_rows(rows):
    random.shuffle(rows)


def connect_to_client():
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(server_address)
    mqtt_client.on_disconnect = on_disconnect


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("sonar connected")
        sys.stdout.flush()


def disconnect_from_client():
    mqtt_client.disconnect()
    sys.exit(0)


def on_disconnect(client, userdata, rc):
    print("sonar disconnected")
    sys.stdout.flush()
    client.connected_flag = False
    client.disconnect_flag = True


def publish(data_to_send):
    try:
        json_data = json.dumps(data_to_send)
        # print("json_data", json_data)
        mqtt_client.publish("from/sensor/sonar", json_data)

    except KeyboardInterrupt:
        mqtt_client.disconnect()
        sys.exit(0)


def send_data():
    if the_control_flag == 1:
        print("sending train data")
        random.shuffle(train_data)
        for i in range(0, min(50, len(train_data))):
            data_to_send = [list_of_feature_names, train_data[i]]
            publish(data_to_send)
            # print("train packet sent")

    elif the_control_flag == 2:
        print("sending test data")
        random.shuffle(test_data)
        for i in range(0, min(50, len(test_data))):
            data_to_send = [list_of_feature_names, test_data[i]]
            publish(data_to_send)
            # print("test packet sent")


def on_message(client, userdata, message):
    global the_control_flag
    # print("received message: ", message.payload.decode("utf-8"))
    print(message)

    msg = str(message.payload.decode("utf-8"))
    print(msg)
    if msg == "send_train_data":
        the_control_flag = 1

    elif msg == "send_test_data":
        the_control_flag = 2

    if the_control_flag == 1 or the_control_flag == 2:
        send_data()
    else:
        print("not sending data yet")


connect_to_client()
mqtt_client.on_message = on_message
mqtt_client.subscribe("from/gateway/control")

chunk_size = 50
seed = sys.argv[2]
dataset = sys.argv[1]
short = sys.argv[3]
sep = sys.argv[4]
# train_data, test_data, list_of_feature_names = prepare_data(data_directory, dataset, seed, short, sep)
#print(data_directory_2, dataset, seed, short, sep)
train_data, test_data, list_of_feature_names = prepare_data_mc(data_directory_2, dataset, seed, short, sep)
#print(list_of_feature_names)
mqtt_client.loop_forever()
'''
try:
    mqtt_client.loop_forever()
except KeyboardInterrupt:
    print("ending sonar_streaming....")
    disconnect_from_client()
'''
