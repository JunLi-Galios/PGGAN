from tensorboardX import SummaryWriter
import numpy as np
import matplotlib.pyplot as plt
import os
import torch
import torch.nn as nn
import time
from scipy.stats import genpareto
import torch.nn.functional as F
from torch.autograd import Variable
from torch import FloatTensor


def convTBNReLU(in_channels, out_channels, kernel_size=4, stride=2, padding=1):
    return nn.Sequential(
        nn.ConvTranspose2d(
            in_channels,
            out_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
        ),
        nn.InstanceNorm2d(out_channels),
        nn.LeakyReLU(0.2, True),
    )


class Generator(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(Generator, self).__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.block1 = convTBNReLU(in_channels, 512, 4, 1, 0)
        self.block2 = convTBNReLU(512, 256)
        self.block3 = convTBNReLU(256, 128)
        self.block4 = convTBNReLU(128, 64)
        self.block5 = nn.ConvTranspose2d(64, out_channels, 4, 2, 1)

    def forward(self, inp):
        out = self.block1(inp)
        out = self.block2(out)
        out = self.block3(out)
        out = self.block4(out)
        return torch.tanh(self.block5(out))

latentdim = 20
G = Generator(in_channels=latentdim, out_channels=1).cuda()
genpareto_params = (1.33, 0, 0.0075761900937239765)
threshold = -0.946046018600464
rv = genpareto(*genpareto_params)

G.load_state_dict(torch.load('DCGAN_1dexpo/G999.pt'))
G.eval()
img_size = [64, 64]
e = torch.distributions.exponential.Exponential(torch.ones([1]))
images = []
count = 0
t = time.time()
while count<100:
    latent = Variable(FloatTensor(torch.randn((100, latentdim, 1, 1)))).cuda()
    image = G(latent)
    e_samples = e.rsample([len(image)]).cuda()
    print('image', image.size())
    print('e_samples', e_samples.size())
    image = image + e_samples[:,:,None,None]
    print('image', image.size())
    images.append(image)
    count += image.shape[0]
    print(time.time() - t)
    images = torch.cat(images, 0)[:100]
    torch.save(images, 'DCGAN_1dexpo.pt')
