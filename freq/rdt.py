import torch

weights = torch.zeros(10)+1
weights[0] = 3
weights[1] = 3
weights = weights/weights.sum()

output = torch.zeros(10)
output[0] = 1
output[2] = 1

function = torch.zeros(10)
function.requires_grad = True

optim = torch.optim.SGD([function], lr=0.1)
sigmoid = torch.nn.Sigmoid()

# MI between input and output

LAMBDA = 3
for itera in range(1000000):
    func_output = sigmoid(function)
    mean_func_output = (func_output*weights).sum()
#    print(mean_func_output)
    marginal_ent = -(mean_func_output * torch.log(mean_func_output) + (1-mean_func_output) * torch.log(1-mean_func_output))
#    print(marginal_ent)
    MI = (weights * (marginal_ent + (func_output * torch.log(func_output) + (1-func_output) * torch.log(1-func_output)))).sum()
    
    Distortion = ((output - func_output).pow(2) * weights).sum()
    

    loss = MI + LAMBDA * Distortion
    optim.zero_grad()
    loss.backward()
    optim.step()
    if itera % 100 == 0:
       print(loss, float(MI), float(Distortion), "Frequent irregular", float(func_output[0]), "Infrequent irregular", float(func_output[2]), "Mean: ", float(mean_func_output))



