<div align="center">

# 🧠 Deep Learning & Neural Networks

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Colab](https://img.shields.io/badge/Google_Colab-F9AB00?style=for-the-badge&logo=googlecolab&logoColor=white)
![Notebooks](https://img.shields.io/badge/Notebooks-2-00e5ff?style=for-the-badge)
![Auto Updated](https://img.shields.io/badge/Auto_Updated-22_Mar_2026_17%3A16_UTC-blueviolet?style=for-the-badge)

**A hands-on exploration of forward propagation, neural network architecture,**
**and the mathematics that power modern AI — built from scratch.**

[📓 Notebooks](#-notebooks) · [🔬 Concepts](#-concepts-covered) · [🚀 Get Started](#-getting-started) · [📂 Structure](#-repository-structure)

> 🤖 _This README is **auto-generated** on every push via GitHub Actions._
> Last updated: **22 Mar 2026 17:16 UTC**

</div>

---

## 📊 At a Glance

| 📓 Notebooks | 🏷️ Topics | 🌐 Language | ⚡ Runtime |
|:---:|:---:|:---:|:---:|
| **2** | **10** | Python 3 | Jupyter / Colab |

---

## 📓 Notebooks

| # | Notebook | Description | Tags | Last Updated |
|---|----------|-------------|------|-------------|
| 1 | [**Alzheimer Dataset Used**](https://github.com/vineetm1204-m/Deep-Learning-And-Neural-Network/blob/main/alzheimer-dataset-used.ipynb) | `from tensorflow.keras.preprocessing.image import ImageDataGenerator
import warnings

# Su… | `data-preprocessing` `CNN` `convolution` `activation-functions` `loss-functions` `optimization` | 2 days ago |
| 2 | [**Forward Propogation Neural Network And Deep Learning**](https://github.com/vineetm1204-m/Deep-Learning-And-Neural-Network/blob/main/forward-propogation%20Neural%20Network%20and%20Deep%20Learning.ipynb) | Deep learning notebook — open to explore. | `forward-propagation` `deep-learning` `neural-network` `numpy` | 2 days ago |

### ▶️ Open in Google Colab

[![Alzheimer Dataset Used](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vineetm1204-m/Deep-Learning-And-Neural-Network/blob/main/alzheimer-dataset-used.ipynb) `alzheimer-dataset-used.ipynb`
[![Forward Propogation Neural Network And Deep Learning](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/vineetm1204-m/Deep-Learning-And-Neural-Network/blob/main/forward-propogation%20Neural%20Network%20and%20Deep%20Learning.ipynb) `forward-propogation Neural Network and Deep Learning.ipynb`

---

## 🔬 Concepts Covered

<details>
<summary><strong>01 · Neural Network Fundamentals</strong></summary><br>

A neural network is a computational graph of interconnected nodes (neurons) arranged in layers.

```
Input Layer → Hidden Layer(s) → Output Layer
```

</details>

<details>
<summary><strong>02 · Forward Propagation</strong></summary><br>

At each layer, forward propagation computes:

```python
Z = np.dot(W, X) + b   # Weighted sum
A = activation(Z)       # Apply activation
```

</details>

<details>
<summary><strong>03 · Weight & Bias Initialization</strong></summary><br>

```python
W = np.random.randn(n_out, n_in) * 0.01  # Break symmetry
b = np.zeros((n_out, 1))                  # Zero biases
```

</details>

<details>
<summary><strong>04 · Activation Functions</strong></summary><br>

| Function | Formula | Use Case |
|----------|---------|----------|
| ReLU | `max(0, z)` | Hidden layers |
| Sigmoid | `1 / (1 + e⁻ᶻ)` | Binary output |
| Softmax | `eᶻⁱ / Σeᶻ` | Multi-class |

</details>

<details>
<summary><strong>05 · Deep vs Shallow Networks</strong></summary><br>

- **Shallow**: 1 hidden layer — simpler, less expressive
- **Deep**: 2+ hidden layers — hierarchical features, needs careful training

</details>

<details>
<summary><strong>06 · Vectorized NumPy Operations</strong></summary><br>

```python
Z   = np.dot(W, X) + b       # Entire batch at once
A   = np.maximum(0, Z)        # ReLU — no loops
sig = 1 / (1 + np.exp(-Z))   # Sigmoid
```

</details>

---

## ⚙️ Tech Stack

![Python](https://img.shields.io/badge/Python_3-3776AB?style=flat-square&logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter_Notebook-F37626?style=flat-square&logo=jupyter&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=flat-square)
![Colab](https://img.shields.io/badge/Google_Colab_Ready-F9AB00?style=flat-square&logo=googlecolab&logoColor=white)

---

## 🚀 Getting Started

**1. Clone the repository**
```bash
git clone https://github.com/vineetm1204-m/Deep-Learning-And-Neural-Network.git
cd Deep-Learning-And-Neural-Network
```

**2. Install dependencies**
```bash
pip install numpy matplotlib jupyter
```

**3. Launch Jupyter**
```bash
jupyter notebook
```

**4. Or open directly in Colab** — click any badge in the [Notebooks](#-notebooks) section above.

---

## 📂 Repository Structure

```
Deep-Learning-And-Neural-Network/
│
├── 📓 alzheimer-dataset-used.ipynb
├── 📓 forward-propogation Neural Network and Deep Learning.ipynb
├── 📄 README.md  ← auto-generated
└── 📁 .github/workflows/update-readme.yml
```

---

## 👤 Author

<table><tr><td align='center'>
<b>Vineet Mishra</b><br>
<sub>BTech CSE · Amity University, Gwalior</sub><br><br>
<a href="https://github.com/vineetm1204-m">
<img src="https://img.shields.io/badge/GitHub-vineetm1204-m-181717?style=flat-square&logo=github" />
</a>
</td></tr></table>

Building at the intersection of machine learning, web development, and agri-tech.
Currently working on **KrishiMitra** (smart farming ML platform) and **ToyBill** (GST billing app).
Member of the **Amity Coding Club**.

---

## 🤝 Contributing

1. Fork the repository
2. Create your branch: `git checkout -b feature/your-notebook`
3. Add your `.ipynb` file
4. Commit: `git commit -m 'Add: <topic> notebook'`
5. Push & open a Pull Request

> The README will **auto-update** to include your notebook on the next push! 🎉

---

## ⭐ Support

If this helped you understand deep learning fundamentals, drop a star!

[![Star on GitHub](https://img.shields.io/github/stars/vineetm1204-m/Deep-Learning-And-Neural-Network?style=social)](https://github.com/vineetm1204-m/Deep-Learning-And-Neural-Network)

---

<div align="center">
  <sub>🤖 Auto-generated by <code>generate_readme.py</code> · 22 Mar 2026 17:16 UTC · <a href='https://github.com/vineetm1204-m'>Vineet Mishra</a> · Amity University, Gwalior</sub>
</div>
