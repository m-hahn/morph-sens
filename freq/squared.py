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

LAMBDA = 2
for itera in range(1000000):
    func_output = sigmoid(function)
    mean_func_output = (func_output*weights).sum()
#    print(mean_func_output)
    marginal_ent = -(mean_func_output * torch.log(mean_func_output) + (1-mean_func_output) * torch.log(1-mean_func_output))
#    print(marginal_ent)
    group1 = torch.zeros(10).bool()
    group1[0] = 1
    group1[3] = 1
    group2 = torch.zeros(10).bool()
    group2[1] = 1
    group2[2] = 1
    MI = (weights[group1] * (func_output[group1] - ((weights[group1]/weights[group1].sum())*output[group1]).sum()).pow(2)).sum()
#    print(func_output[group1], weights[group1]/weights[group1].sum(), output[group1], ((weights[group1]/weights[group1].sum())*output[group1]).sum())
    MI += (weights[group2] * (func_output[group2] - ((weights[group2]/weights[group2].sum())*output[group2]).sum()).pow(2)).sum()

#    MI = (weights * (func_output - (output*weights).sum()).pow(2)).sum()
    Distortion = ((output - func_output).pow(2) * weights).sum()
    

    loss = MI + LAMBDA * Distortion
    optim.zero_grad()
    loss.backward()
    optim.step()
    if itera % 100 == 0:
       print(loss, float(MI), float(Distortion), "Frequent irregular", float(func_output[0]), "Infrequent irregular", float(func_output[2]), "Mean: ", float(mean_func_output))



