import numpy as np
import os


weight_folder = 'weights'
memdata_folder = 'MemData'


if not os.path.exists(memdata_folder):
    os.makedirs(memdata_folder)


weights_np = np.load(os.path.join(weight_folder, 'body.bottleneck9.expand.0.weight.npy'))

positive_values = np.where(weights_np >= 0, weights_np, 6.2893081e-14)
negative_values = np.where(weights_np < 0, -weights_np, 6.2893081e-14)
positive_values = 1 / (15900 * positive_values) - 1 / 159
positive_values = np.round(positive_values, 6)
negative_values = 1 / (15900 * negative_values) - 1 / 159
negative_values = np.round(negative_values, 6)


np.save(os.path.join(memdata_folder, 'positive_input_layer.body.bottleneck9.expand.0.weight.npy'), positive_values)
np.save(os.path.join(memdata_folder, 'negative_input_layer.body.bottleneck9.expand.0.weight.npy'), negative_values)

