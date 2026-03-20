<div align="center">

# 🧠 Deep Learning & Neural Networks

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Colab](https://img.shields.io/badge/Google_Colab-F9AB00?style=for-the-badge&logo=googlecolab&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-00e5ff?style=for-the-badge)

**A hands-on exploration of forward propagation, neural network architecture,
and the mathematics that power modern AI — built from scratch.**

[📓 Open Notebook](#-notebooks) · [🚀 Get Started](#-getting-started) · [🔬 Concepts](#-concepts-covered)

</div>

---

## 📁 Notebooks

| File | Description | Topics |
|------|-------------|--------|
| [`forward-propogation Neural Network and Deep Learning.ipynb`](./forward-propogation%20Neural%20Network%20and%20Deep%20Learning.ipynb) | Implements forward propagation from the ground up through a deep neural network | Forward Pass, Activation Functions, Weight Init, NumPy |

---

## 🔬 Concepts Covered

<details>
<summary><strong>01 · Neural Network Fundamentals</strong></summary>
<br>

A neural network is a computational graph of interconnected nodes (neurons) arranged in layers. Each neuron computes a weighted sum of its inputs and passes it through an activation function.

```
Input Layer → Hidden Layer(s) → Output Layer
```

</details>

<details>
<summary><strong>02 · Forward Propagation</strong></summary>
<br>

Forward propagation is the process of passing input data through the network to produce a prediction. At each layer:

```python
Z = np.dot(W, X) + b   # Weighted sum
A = activation(Z)       # Apply activation function
```

This happens sequentially from the input layer to the output layer.

</details>

<details>
<summary><strong>03 · Weights & Bias Initialization</strong></summary>
<br>

Proper initialization is critical to training stability:

```python
W = np.random.randn(n_out, n_in) * 0.01   # Small random weights
b = np.zeros((n_out, 1))                   # Zero biases
```

Poor initialization can cause **vanishing** or **exploding gradients**.

</details>

<details>
<summary><strong>04 · Activation Functions</strong></summary>
<br>

Activation functions introduce non-linearity, enabling networks to learn complex patterns.

| Function | Formula | Use Case |
|----------|---------|----------|
| ReLU | `max(0, z)` | Hidden layers |
| Sigmoid | `1 / (1 + e⁻ᶻ)` | Binary output |
| Softmax | `eᶻⁱ / Σeᶻ` | Multi-class output |

</details>

<details>
<summary><strong>05 · Deep vs Shallow Networks</strong></summary>
<br>

- **Shallow**: 1 hidden layer — simple, fast, limited representation power
- **Deep**: 2+ hidden layers — hierarchical feature learning, requires careful training (gradient issues)

Deep networks can represent more complex functions with fewer total neurons.

</details>

<details>
<summary><strong>06 · Matrix Operations in NumPy</strong></summary>
<br>

All neural network math is vectorized using NumPy for efficiency:

```python
import numpy as np

Z = np.dot(W, X) + b          # Vectorized weighted sum
A = np.maximum(0, Z)           # ReLU — no Python loops needed
sig = 1 / (1 + np.exp(-Z))    # Sigmoid
```

Broadcasting handles entire batches simultaneously.

</details>

---

## ⚙️ Tech Stack

![Python](https://img.shields.io/badge/Python_3-3776AB?style=flat-square&logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter_Notebook-F37626?style=flat-square&logo=jupyter&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=flat-square&logo=plotly&logoColor=white)
![Colab](https://img.shields.io/badge/Google_Colab_Ready-F9AB00?style=flat-square&logo=googlecolab&logoColor=white)

---

## 🚀 Getting Started

**Step 1 — Clone the repository**
```bash
git clone https://github.com/vineetm1204-m/Deep-Learning-And-Neural-Network.git
cd Deep-Learning-And-Neural-Network
```

**Step 2 — Install dependencies**
```bash
pip install numpy matplotlib jupyter
```

**Step 3 — Launch the notebook**
```bash
jupyter notebook "forward-propogation Neural Network and Deep Learning.ipynb"
```

**Step 4 — Run all cells**

Go to **Kernel → Restart & Run All** to execute from scratch and follow the complete forward propagation flow.

> 💡 **Prefer Colab?** Click the badge below to open directly in your browser — no setup needed.
>
> [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vineetm1204-m/Deep-Learning-And-Neural-Network/blob/main/forward-propogation%20Neural%20Network%20and%20Deep%20Learning.ipynb)

---

## 📂 Repository Structure

```
Deep-Learning-And-Neural-Network/
│
├── forward-propogation Neural Network and Deep Learning.ipynb
│   └── Forward pass implementation with activations & matrix ops
│
└── README.md
```

---

## 👤 Author

<table>
  <tr>
    <td align="center">
      <b>Vineet Mishra</b><br>
      <sub>BTech CSE · Amity University, Gwalior</sub><br><br>
      <a href="https://github.com/vineetm1204-m">
        <img src="https://img.shields.io/badge/GitHub-vineetm1204--m-181717?style=flat-square&logo=github" />
      </a>
    </td>
  </tr>
</table>

Building at the intersection of machine learning, web development, and agri-tech.
Currently working on **KrishiMitra** (smart farming ML platform) and **ToyBill** (GST billing app).
Member of the **Amity Coding Club**.

---

## 🤝 Contributing

Contributions, issues and feature requests are welcome!

1. Fork the repository
2. Create your branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## ⭐ Support

If this helped you understand deep learning fundamentals, consider giving it a **star** — it means a lot!

[![Star on GitHub](https://img.shields.io/github/stars/vineetm1204-m/Deep-Learning-And-Neural-Network?style=social)](https://github.com/vineetm1204-m/Deep-Learning-And-Neural-Network)

---

<div align="center">
  <sub>Made with ❤️ by <a href="https://github.com/vineetm1204-m">vineetm1204-m</a> · Amity University Gwalior</sub>
</div>
