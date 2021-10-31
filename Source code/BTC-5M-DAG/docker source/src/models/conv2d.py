import torch
from torch import nn

class Conv2D(nn.Module):
    def __init__(self, 
                 size_x, 
                 size_y,
                 out1=16, 
                 out2=32, 
                 linear_out1=32,
                 no_channels=1,
                 drop_one=.25, 
                 drop_two=.5,
                 dtype=torch.float64,
                 kernel_size=(3, 3),
                 pooling_size=2,
                 loss_fun=torch.nn.MSELoss(),
                 conv_out=512):
        super(Conv2D, self).__init__()
        input_shape = (size_x, size_y, 1)
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels=no_channels,
                out_channels=out1,
                kernel_size=kernel_size),
            nn.ReLU(),
            nn.Conv2d(in_channels=out1,
                out_channels=out2,        
                kernel_size=kernel_size),
            nn.ReLU(),
            nn.MaxPool2d(pooling_size),
            nn.Dropout(drop_one),
            nn.Flatten())
      
        self.linear = nn.Sequential(
            nn.Linear(conv_out, linear_out1),
            nn.ReLU(),
            nn.Dropout(drop_two),
            nn.Linear(linear_out1, 1)
        )
        self.loss_fun = loss_fun
        self.to(dtype=dtype)

    def forward(self, X):
        X = self.conv(X)
        X = self.linear(X)
        return X

    def loss(self, out, targets):
        return self.loss_fun(out, targets)