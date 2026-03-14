# InfiniBand Connectivity Specifications for ArchiMeades DGX Cluster

> **Verified against NVIDIA documentation** (DGX User Guides, DGX SuperPOD/BasePOD Reference Architectures, Quantum switch datasheets). Last verified: 2025-03-14.

---

## 1. DGX Node Connectivity (by model)

### DGX A100

| Spec | Value |
|------|-------|
| **Cluster NICs** | Up to 10× ConnectX-6 or ConnectX-7 single-port (640GB model); up to 9× (320GB model) |
| **Per-port speed** | 200 Gb/s (HDR InfiniBand) or 200GbE |
| **ConnectX-6 VPI** | Dual protocol: InfiniBand HDR (200 Gb/s) or Ethernet 10/25/50/100/200 Gb/s |
| **ConnectX-7 single-port** | InfiniBand only (200 Gb/s HDR) |
| **Storage NIC** | 1× ConnectX-6/7 dual-port: 200 Gb/s InfiniBand or 200GbE |
| **Form factor** | QSFP56 for HDR |
| **RDMA** | Yes (GPUDirect RDMA, GPUDirect Storage) |
| **Latency** | Sub-600 ns (ConnectX-6) |

*Source: [NVIDIA DGX A100 User Guide](https://docs.nvidia.com/dgx/dgxa100-user-guide/introduction-to-dgxa100.html)*

### DGX H100 / H200

| Spec | Value |
|------|-------|
| **Cluster NICs** | 8× ConnectX-7 single-port InfiniBand |
| **Per-port speed** | 400 Gb/s (NDR InfiniBand) |
| **ConnectX-7** | InfiniBand only (NDR 400 Gb/s) |
| **Form factor** | OSFP |
| **RDMA** | Yes (GPUDirect RDMA, GPUDirect Storage) |
| **Features** | Adaptive routing, SHARP, SHIELD (dynamic healing) |

*Source: [NVIDIA DGX H100 User Guide](https://docs.nvidia.com/dgx/dgxh100-user-guide/introduction-to-dgxh100.html), [DGX SuperPOD H100 Network Fabrics](https://docs.nvidia.com/dgx-superpod/reference-architecture-scalable-infrastructure-h100/latest/network-fabrics.html)*

---

## 2. InfiniBand Speed Nomenclature

| Generation | Speed | Lanes | Form factor | Typical use |
|------------|-------|-------|-------------|-------------|
| **HDR** | 200 Gb/s | 4× 50 Gb/s PAM4 | QSFP56 | DGX A100 |
| **NDR** | 400 Gb/s | 4× 100 Gb/s PAM4 | OSFP, QSFP112 | DGX H100 |
| **NDR200** | 200 Gb/s | 2× 100 Gb/s | OSFP (port-split) | — |

*Source: [NVIDIA NDR Overview](https://docs.nvidia.com/dgx-superpod/design-guide-cabling-data-centers/latest/ndr-overview.html), [InfiniBand HDR vs NDR](https://www.philisun.com/technical-analysis/what-is-the-difference-between-ndr-and-hdr-infiniband/)*

---

## 3. NVIDIA Quantum InfiniBand Switches

### Quantum QM8700 (HDR 200 Gb/s) — for DGX A100

| Spec | Value |
|------|-------|
| **Port speed** | 200 Gb/s per port |
| **Port count** | 40 ports @ 200 Gb/s (or 80 @ 100 Gb/s via port-split) |
| **Connector** | QSFP56 |
| **Aggregate throughput** | 16 Tb/s bidirectional |
| **Form factor** | 1U |
| **Features** | Adaptive routing, SHARP, self-healing, RDMA |

*Source: [NVIDIA Quantum QM8700](https://www.nvidia.com/en-eu/networking/infiniband/qm8700/), [QM87xx User Manual](https://docs.nvidia.com/networking/display/qm87xx)*

### Quantum-2 QM9700 (NDR 400 Gb/s) — for DGX H100

| Spec | Value |
|------|-------|
| **Port speed** | 400 Gb/s per port |
| **Port count** | 64 ports @ 400 Gb/s (or 128 @ 200 Gb/s via port-split) |
| **Connector** | 32 OSFP cages |
| **Aggregate throughput** | 51.2 Tb/s bidirectional |
| **Form factor** | 1U |
| **Port-to-port latency** | < 90 ns |
| **Features** | SHARPv3, RDMA, GPUDirect RDMA, adaptive routing, self-healing |

*Source: [NVIDIA Quantum-2 QM9700](https://docs.nvidia.com/networking/display/qm97x0pub/specifications), [Dell Technologies QM9700 Datasheet](https://www.delltechnologies.com/asset/en-us/products/networking/technical-support/nvidia-quantum-2-qm9700-series-datasheet.pdf)*

---

## 4. Fabric Topology for 16–64 Nodes

### DGX H100 SuperPOD (NDR 400 Gb/s)

| Scale | Nodes | SU count | Leaf switches | Spine switches | Compute cables | Spine–leaf cables |
|-------|-------|----------|---------------|----------------|----------------|-------------------|
| 16 nodes | 16 | Partial (1 SU) | 8 | 4 | 252* | 256* |
| 64 nodes | 63 | 2 | 16 | 8 | 508 | 512 |
| 127 nodes | 127 | 4 | 32 | 16 | 1020 | 1024 |

*Per NVIDIA: build full SU fabric and leave unused portions for optimal routing. 1 SU = 32 nodes (31 compute + 1 UFM); 16 nodes = half of 1 SU.*

*Source: [DGX SuperPOD H100 Network Fabrics, Table 4](https://docs.nvidia.com/dgx-superpod/reference-architecture-scalable-infrastructure-h100/latest/network-fabrics.html)*

### DGX A100 BasePOD (HDR 200 Gb/s)

| Scale | Switch | Notes |
|-------|--------|-------|
| 4–16 nodes | QM8700 HDR 200 Gb/s | Single switch or small fat-tree for 16 nodes |
| 16+ nodes | Multiple QM8700 | Leaf–spine topology per BasePOD sizing |

*Source: [DGX BasePOD A100 Architecture](https://docs.nvidia.com/dgx-basepod/deployment-guides/dgx-basepod-a100/latest/architecture.html)*

---

## 5. Cables and Transceivers

| DGX model | InfiniBand speed | Cable/transceiver type |
|-----------|------------------|------------------------|
| DGX A100 | HDR 200 Gb/s | QSFP56 (AOC or DAC) |
| DGX H100 | NDR 400 Gb/s | OSFP (AOC or DAC) |

*Verify compatibility with ConnectX firmware via [Mellanox Firmware Release](https://docs.nvidia.com/networking/category/adapterfw).*

---

## 6. Software Requirements

- **MOFED** (Mellanox OpenFabrics Enterprise Distribution) or **NVIDIA MLNX_OFED**
- **Subnet manager** (on-board or UFM for larger clusters)
- **DGX OS** includes MOFED, MST, DCGM pre-installed

---

## 7. Summary for ArchiMeades (16 → 64 nodes)

| Component | 16 nodes (DGX A100) | 16 nodes (DGX H100) | 64 nodes (DGX H100) |
|-----------|---------------------|---------------------|----------------------|
| **Switch** | QM8700 HDR (40× 200G) | QM9700 NDR (64× 400G) | 16 leaf + 8 spine QM9700 |
| **InfiniBand** | 200 Gb/s HDR | 400 Gb/s NDR | 400 Gb/s NDR |
| **Ports per node** | 8–10 | 8 | 8 |
| **Topology** | Single or small fat-tree | 8 leaf + 4 spine | 16 leaf + 8 spine |

---

*For deployment details, see NVIDIA DGX BasePOD and DGX SuperPOD deployment guides.*
