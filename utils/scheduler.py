import torch
from torch.optim.lr_scheduler import (
    CosineAnnealingLR, StepLR, ExponentialLR, 
    ReduceLROnPlateau, OneCycleLR
)
import math

def get_scheduler(optimizer, scheduler_type: str, num_epochs: int, 
                 warmup_epochs: int = 0, **kwargs):
    """Get learning rate scheduler"""
    
    if scheduler_type == 'cosine':
        if warmup_epochs > 0:
            return CosineAnnealingWarmupRestarts(
                optimizer, 
                first_cycle_steps=num_epochs,
                warmup_steps=warmup_epochs,
                **kwargs
            )
        else:
            return CosineAnnealingLR(optimizer, T_max=num_epochs, **kwargs)
    
    elif scheduler_type == 'step':
        step_size = kwargs.get('step_size', num_epochs // 3)
        gamma = kwargs.get('gamma', 0.1)
        return StepLR(optimizer, step_size=step_size, gamma=gamma)
    
    elif scheduler_type == 'exponential':
        gamma = kwargs.get('gamma', 0.95)
        return ExponentialLR(optimizer, gamma=gamma)
    
    elif scheduler_type == 'plateau':
        return ReduceLROnPlateau(optimizer, mode='max', patience=5, **kwargs)
    
    elif scheduler_type == 'onecycle':
        return OneCycleLR(
            optimizer, 
            max_lr=optimizer.param_groups[0]['lr'],
            epochs=num_epochs,
            steps_per_epoch=kwargs.get('steps_per_epoch', 100),
            **kwargs
        )
    
    else:
        raise ValueError(f"Unknown scheduler type: {scheduler_type}")

class CosineAnnealingWarmupRestarts(torch.optim.lr_scheduler._LRScheduler):
    """Cosine annealing with warmup restarts"""
    
    def __init__(self, optimizer, first_cycle_steps: int, cycle_mult: float = 1.0,
                 max_lr: float = 0.1, min_lr: float = 0.001, warmup_steps: int = 0,
                 gamma: float = 1.0, last_epoch: int = -1):
        
        self.first_cycle_steps = first_cycle_steps
        self.cycle_mult = cycle_mult
        self.base_max_lr = max_lr
        self.max_lr = max_lr
        self.min_lr = min_lr
        self.warmup_steps = warmup_steps
        self.gamma = gamma
        
        self.cur_cycle_steps = first_cycle_steps
        self.cycle = 0
        self.step_in_cycle = last_epoch
        
        super().__init__(optimizer, last_epoch)
        
        # Set learning rates manually
        self.init_lr()
    
    def init_lr(self):
        self.base_lrs = []
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = self.min_lr
            self.base_lrs.append(self.min_lr)
    
    def get_lr(self):
        if self.step_in_cycle == -1:
            return self.base_lrs
        elif self.step_in_cycle < self.warmup_steps:
            return [(self.max_lr - base_lr) * self.step_in_cycle / self.warmup_steps + base_lr
                    for base_lr in self.base_lrs]
        else:
            return [base_lr + (self.max_lr - base_lr) * 
                   (1 + math.cos(math.pi * (self.step_in_cycle - self.warmup_steps) / 
                                (self.cur_cycle_steps - self.warmup_steps))) / 2
                   for base_lr in self.base_lrs]
    
    def step(self, epoch=None):
        if epoch is None:
            epoch = self.last_epoch + 1
            self.step_in_cycle = self.step_in_cycle + 1
            if self.step_in_cycle >= self.cur_cycle_steps:
                self.cycle += 1
                self.step_in_cycle = self.step_in_cycle - self.cur_cycle_steps
                self.cur_cycle_steps = int((self.cur_cycle_steps - self.warmup_steps) * self.cycle_mult) + self.warmup_steps
        else:
            if epoch >= self.first_cycle_steps:
                if self.cycle_mult == 1.0:
                    self.step_in_cycle = epoch % self.first_cycle_steps
                    self.cycle = epoch // self.first_cycle_steps
                else:
                    n = int(math.log((epoch / self.first_cycle_steps * (self.cycle_mult - 1) + 1), self.cycle_mult))
                    self.cycle = n
                    self.step_in_cycle = epoch - int(self.first_cycle_steps * (self.cycle_mult ** n - 1) / (self.cycle_mult - 1))
                    self.cur_cycle_steps = self.first_cycle_steps * self.cycle_mult ** n
            else:
                self.cur_cycle_steps = self.first_cycle_steps
                self.step_in_cycle = epoch
                
        self.max_lr = self.base_max_lr * (self.gamma ** self.cycle)
        self.last_epoch = math.floor(epoch)
        
        for param_group, lr in zip(self.optimizer.param_groups, self.get_lr()):
            param_group['lr'] = lr
