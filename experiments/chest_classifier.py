import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
import torchvision.transforms as transforms
from torchvision.models import inception_v3, resnet18
from torch import optim
import sys
import os
from collections import OrderedDict


data_path='/home/tank/Downloads/chest_xray/chest_xray'

sys.path.insert(0, "../")
from kac_independence_measure import KacIndependenceMeasure
from torch.nn.functional import *

class ResNet18(nn.Module):
    
    def __init__(self, layer_numbers):
        super().__init__()
        self.layer_numbers = layer_numbers # indices of layers whose activations are needed
        self.layer_acts = OrderedDict()
        #self.resnet_18 = inception_v3(pretrained=True, aux_logits=False) 
        self.resnet_18 = resnet18(pretrained=True) #, aux_logits=True)
        self.forward_hooks = []
        
        #register hooks
        for layer_num, layer_name in enumerate(self.resnet_18._modules.keys()):
            if layer_num in layer_numbers:
                print("Layer num {}, name: {}, shape {}".format(layer_num, layer_name, ''))
                self.forward_hooks.append(getattr(self.resnet_18, layer_name).register_forward_hook(self.get_activations(layer_name)))
    
    #Defining hook to get intermediate features     
    def get_activations(self, layer_name):
        def hook(module, input, output):
            self.layer_acts[layer_name] = output
        return hook
    
    #forward pass
    def forward(self, x):
        out = self.resnet_18(x)
        #don't need output values
        return self.layer_acts


#os.listdir('./chest-xray-pneumonia/')
#image = './chest-xray-pneumonia/train/normal/IM-0115-0001.jpeg'
#img = plt.imread(image)
#plt.imshow(img, cmap='gray')

kim = KacIndependenceMeasure(512, 1, lr=0.007, input_projection_dim = 256, weight_decay=0.01) #0.007


train_transform = transforms.Compose([transforms.Grayscale(num_output_channels=3), 
                                      transforms.Resize((224,224)),
                                      transforms.RandomHorizontalFlip(),
                                      transforms.ColorJitter(brightness=1, contrast=1, saturation=1),
                                      transforms.ToTensor(),
                                      transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

test_transform = transforms.Compose([transforms.Grayscale(num_output_channels=3), 
                                     transforms.Resize((224,224)),
                                     transforms.ToTensor(),
                                     transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
training_dataset = ImageFolder(data_path + '/train', transform=train_transform)
validation_dataset = ImageFolder(data_path + '/val', transform=train_transform)
testing_dataset = ImageFolder(data_path + '/test', transform=test_transform )
len_train= len(training_dataset.samples)
len_test= len(testing_dataset.samples)
len_val= len(validation_dataset.samples)
print(len_train)
print(len_test)
print(len_val)

train_loader = DataLoader(dataset=training_dataset, batch_size=64, shuffle=True)
val_loader = DataLoader(dataset=validation_dataset, shuffle= True)
test_loader = DataLoader(dataset= testing_dataset, shuffle=False)

z_key = 2


#model = inception_v3(pretrained=True, aux_logits=False)
required_layers = [1, z_key, 17]
model = ResNet18(layer_numbers=required_layers) #pretrained=True) #, aux_logits=False)


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model.to(device)
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.AdamW(params=model.parameters(), lr = 0.0002, weight_decay=0.00001)
number_of_epoch = 7

train_loss = []
test_loss = []
train_accuracy = []
test_accuracy = []

num_kac_iters = 200
optimize_kac_every_iters = 500

for epoch in range(number_of_epoch):
    
    train_correct = 0
    test_correct = 0
    train_iter_loss = 0.0
    test_iter_loss = 0.0
    train_iteration = 0
    test_iteration = 0
    
    model.train()
    iteration = 0
    for data,label in train_loader:
        
        optimizer.zero_grad()
        data = data.to(device)
        label = label.to(device)
        
        pred = model(data)
        breakpoint()
        loss = loss_fn(pred[0], label)
        loss.backward()
        optimizer.step()
        
        train_iter_loss += loss.item()
        train_iteration += 1
        
        _, predicted = torch.max(pred, 1)
        train_correct += (predicted == label).sum()
        iteration = iteration + 1

        if iteration % optimize_kac_every_iters == 0:
            # optimize kac_im
            pass
        
    train_loss.append(train_iter_loss/train_iteration)
    train_accuracy.append(100*float(train_correct)/len_train)
    
    torch.save({
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'loss': train_loss,
        }, format("chest_checkpoint_{}.pt".format(epoch)))

    model.eval()
    with torch.no_grad():
        for data,label in val_loader:
        
            data = data.to(device)
            label = label.to(device)
        
            pred = model(data)
            loss = loss_fn(pred, label)
        
            test_iter_loss += loss.item()
            test_iteration += 1
        
            _, predicted = torch.max(pred, 1)
            test_correct += (predicted == label).sum()
        
    test_loss.append(test_iter_loss/test_iteration)
    test_accuracy.append(100*float(test_correct)/len_val)
    
    print ('Epoch {}/{}, Training Loss: {:.3f}, Training Accuracy: {:.3f}, Validation Loss: {:.3f}, Validation Acc: {:.3f}'
           .format(epoch+1, number_of_epoch, train_loss[-1], train_accuracy[-1], test_loss[-1], test_accuracy[-1]))


corrected = 0

model.eval()
for data, label in test_loader:
    data = data.to(device)
    label = label.to(device)
    
    pred = model(data)
    _, predicted = torch.max(pred, 1)
    
    corrected += (predicted == label).sum()
    
accuracy = 100 * float(corrected)/ len_test

print(f'Test accuracy is {accuracy :.3f}')
