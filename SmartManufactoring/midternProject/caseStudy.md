# CMP Dispatching at SSMC: Distilled Knowledge from Two Case Documents

## 1. Executive Summary

This case studies the design of a **dispatching algorithm for the Chemical-Mechanical Planarization (CMP) stage** in a semiconductor fab, specifically at **Systems on Silicon Manufacturing Company (SSMC)** in Singapore. The core challenge is that CMP is not an isolated machine group; it is a **tightly coupled multi-stage system** consisting of **sorters, CMP tools, cleaners, water tanks, and cassette resources**, all constrained by **queue-time windows, finite buffers, and changeover times**. Because of these interactions, simple local dispatching rules are not enough. The dispatching logic must coordinate the entire stage as one integrated system. :contentReference[oaicite:0]{index=0} :contentReference[oaicite:1]{index=1}

The key managerial insight is this:

> **The real problem is not only “which lot should go next,” but “which lot should be released now so that downstream resources, queue-time constraints, and future capacity states remain feasible.”** :contentReference[oaicite:2]{index=2} :contentReference[oaicite:3]{index=3}

---

## 2. Business and Operational Context

SSMC is a semiconductor foundry joint venture of **NXP Semiconductors** and **TSMC**, launched in Singapore in 2000. It manufactures a wide range of products such as **embedded flash, analog mixed signal, power devices, and CMOS ICs**. In this environment, **cycle time** and **throughput** are critical competitive metrics. The case emphasizes that in stochastic manufacturing systems with fixed capacity, better performance depends on reducing variability, and one major driver of variability at workstations is the **dispatching policy**. :contentReference[oaicite:4]{index=4}

The fab runs **24/7**, and many dispatching decisions had historically depended on operators. Because operator turnover was high, SSMC started building a fab dispatching system (**DSP**) in 2011 to reduce reliance on operator experience. CMP later became the fab bottleneck, making it a high-impact target for dispatching improvement. :contentReference[oaicite:5]{index=5}

---

## 3. Why CMP Is Operationally Difficult

The slides frame semiconductor fabs as **complex queueing networks** with **multiple products and different requirements**, and the case document shows why CMP is one of the most difficult parts of that network. :contentReference[oaicite:6]{index=6} :contentReference[oaicite:7]{index=7}

CMP is difficult because:

1. **It is a bottleneck process** with very high utilization.  
2. **Its downstream clean step is time-sensitive** because slurry must be removed before it hardens.  
3. **Intermediate storage is limited and specialized**, especially water tanks.  
4. **Tools can be reconfigured**, but changeovers take hours.  
5. **Material handling changes wafer identity/visibility**, reducing responsiveness after sorting.  
6. **Batching effects matter**, since CMP processes lots in a serial-batch structure. :contentReference[oaicite:8]{index=8} :contentReference[oaicite:9]{index=9}

So CMP dispatching is a **resource-coupling problem**, not just a sequencing problem.

---

## 4. Physical and Process Flow of the CMP Stage

The CMP stage includes three major steps:

1. **Sort**
2. **CMP**
3. **Clean** :contentReference[oaicite:10]{index=10} :contentReference[oaicite:11]{index=11}

### 4.1 Sort
Sorters change wafers from **normal cassettes** into **Teflon cassettes**, because CMP requires Teflon cassettes. The sort step is fast, around **3 minutes per lot**, generally less than 5 minutes. The case document states there are **4 identical sorters**. :contentReference[oaicite:12]{index=12}

### 4.2 CMP
CMP is the polishing stage. It uses both chemical slurry and mechanical polishing to planarize wafer surfaces. The process time is about **45 minutes per lot**. The CMP tools are divided into three groups:

- **APT**: 4 tools  
- **APX**: 15 tools  
- **APW**: 15 tools :contentReference[oaicite:13]{index=13}

The slides also note:

- **Process time ~ 45 min**
- **Cascading: 3 min saving**
- **Serial batch size: 4**
- **Lot size: 25 wafers max** :contentReference[oaicite:14]{index=14}

This means CMP is a **serial batching machine**: up to **4 lots** can be loaded together, and when lots are processed continuously, each additional lot can save about **3 minutes** due to overlap between wafers of adjacent lots. This is important because dispatching decisions affect not only due-date performance but also **effective capacity through batching efficiency**. :contentReference[oaicite:15]{index=15}

### 4.3 Clean
After CMP, wafers go to cleaners to remove chemical slurry. Cleaning takes around **30 minutes per lot**. Cleaner groups are:

- **AST/ASX** for jobs from **APT/APX**
- **ASW** for jobs from **APW** :contentReference[oaicite:16]{index=16} :contentReference[oaicite:17]{index=17}

Within ASW there are two sub-groups:

- **ASW_1**: alkaline solution (**NH4OH**)
- **ASW_2**: acid solution (**HF**) :contentReference[oaicite:18]{index=18} :contentReference[oaicite:19]{index=19}

---

## 5. Resource Structure and Constraints

The dispatching problem is driven by four major constraint classes.

### 5.1 Queue-Time / Time-Window Constraint
Because slurry must be removed before it hardens, there is a maximum allowed time between CMP and clean:

- **APT/APX → AST/ASX**: **6 hours**
- **APW → ASW**: **2 hours** :contentReference[oaicite:20]{index=20}

If the queue time exceeds the limit, lots may need to be **reworked or scrapped**. This is one of the most important constraints because it effectively limits how much WIP can safely sit after CMP. :contentReference[oaicite:21]{index=21}

### 5.2 Water Tank Capacity
WIP between CMP and cleaners must be stored in **water tanks** to maintain slurry moisture and prevent hardening. There are **8 water tanks** with total capacity **52 lots**:

- 6 tanks hold 6 lots each
- 2 tanks hold 8 lots each :contentReference[oaicite:22]{index=22}

Water tanks are not fully interchangeable:

- Lots from **APT/APX** can share the same tank type
- Lots from **APW** can share the same tank type
- But **APT/APX lots and APW lots cannot be stored in the same water tank** :contentReference[oaicite:23]{index=23}

Reassigning tank arrangements requires **0.5 hours** of changeover. :contentReference[oaicite:24]{index=24} :contentReference[oaicite:25]{index=25}

### 5.3 Cleaner Capacity and Changeovers
Cleaners are specialized. Some can back up others, but changeovers take time:

- Some **ASX/ASW** switches take about **2 to 6 hours**
- **ASW_1 ↔ ASW_2** switching takes **6 hours** :contentReference[oaicite:26]{index=26}

The slides further simplify this as cleaner-related changeovers of roughly **1.5 to 6 hours**. :contentReference[oaicite:27]{index=27}

### 5.4 Teflon Cassette / Intermediate Buffer Constraints
The slides state there are **200 Teflon cassettes shared across all three processes**, and the sorter-to-CMP buffers are finite. :contentReference[oaicite:28]{index=28}  
The case document also notes that space before sorters can be treated as effectively infinite, but space after sorters and before CMP is limited. :contentReference[oaicite:29]{index=29}

---

## 6. APW as the Most Illustrative Subproblem

The APW path is especially useful for understanding why dispatching is hard. The slides isolate APW and list these constraints:

1. **Time window: 2 hours between APW and ASW**
2. **DNS capacity: NH4OH (x7) and HF (x4)**
3. **Water tanks: 52 shared space**
4. **Teflon cassettes: 200 shared space** :contentReference[oaicite:30]{index=30}

This shows that APW is not only limited by its own machine capacity; it is also exposed to:

- downstream chemical-route imbalance,
- finite shared intermediate storage,
- long changeover delays,
- and shared carrier resources.

In practice, APW can become blocked not because APW itself is down, but because **its downstream path is infeasible or congested**. That is the hallmark of a coupled, constrained production stage. :contentReference[oaicite:31]{index=31} :contentReference[oaicite:32]{index=32}

---

## 7. Current Practice Before the New Pull Logic

Before the proposed pull-oriented dispatching system, SSMC used a **push-oriented approach**:

- Sorters pushed jobs into CMP
- Jobs were released according to **pre-determined move targets**
- The policy did **not** adequately consider **real-time WIP congestion downstream** :contentReference[oaicite:33]{index=33}

This created a mismatch between upstream release and downstream feasibility. In other words, lots were being released because there was nominal local space, not because the entire stage could absorb them without later blocking.

The case explicitly argues for moving from a **push system** to a **pull system with real-time WIP level control**. The pull logic is inspired by Toyota-style thinking: production should respond to actual downstream consumption and current system state, not just forecasts or upstream release targets. :contentReference[oaicite:34]{index=34}

---

## 8. Quantitative Picture of Current Performance

The slide deck provides utilization, average WIP, and average queue-time (QT) figures for current practice:

### CMP
- **APT**: Utilization **91.95%**, Avg WIP **13.02 × 23**, Avg QT **4.28**
- **APX**: Utilization **94.37%**, Avg WIP **32.30 × 23**, Avg QT **3.57**
- **APW**: Utilization **94.41%**, Avg WIP **16.90 × 23**, Avg QT **3.05** :contentReference[oaicite:35]{index=35}

### Cleaners
- **AST**: Utilization **89.85%**, Avg WIP **2.02 × 23**, Avg QT **0.66**
- **ASX**: Utilization **88.19%**, Avg WIP **11.85 × 23**, Avg QT **0.75**
- **ASW_1 (NH4OH)**: Utilization **85.76%**, Avg WIP **7.20 × 23**, Avg QT **0.67**
- **ASW_2 (HF)**: Utilization **85.10%**, Avg WIP **3.86 × 23**, Avg QT **0.69** :contentReference[oaicite:36]{index=36}

### Interpretation
These numbers suggest three important operational realities:

1. **CMP is highly utilized**, so even small blocking losses are expensive.
2. **Cleaner utilization is lower than CMP utilization**, which means system loss may come not from nominal cleaner capacity alone, but from **mismatch, routing, queue-time windows, and finite buffer interactions**.
3. **WIP is substantial**, which is consistent with the case’s point that queued wafers at CMP can rise dramatically and inflate cycle time. :contentReference[oaicite:37]{index=37} :contentReference[oaicite:38]{index=38}

---

## 9. Root Problems Identified in the Case

Both documents align on three central problems.

### 9.1 CMP Capacity Loss
CMP can be blocked by downstream cleaners or by lack of feasible downstream storage. In the APW example, if too many lots for one cleaner type occupy the water tanks, the other route may become space-constrained, causing blocking upstream. The slides also mention that needed lots such as **NH4OH jobs** may not be sortable because equipment is occupied by other types such as **HF lots** or because Teflon cassettes are limited. :contentReference[oaicite:39]{index=39} :contentReference[oaicite:40]{index=40}

### 9.2 Passive Capacity Planning
Some tools can be reconfigured to support another route, but the switch takes **hours**. Historically, switching decisions were often made **too late**. This means capacity planning was reactive rather than proactive. A good dispatching system must therefore consider not just immediate queue status but also **foreseeable future imbalance**. :contentReference[oaicite:41]{index=41}

### 9.3 Poor Responsiveness
After sorting, wafers lose the easy barcode-based identification associated with normal cassettes. As a result, lots are harder to distinguish, and downstream processing tends to follow **FIFO**. That means a delayed urgent lot cannot easily jump ahead once it enters the post-sort pipeline. The old system therefore lacked agility in reacting to urgent or late jobs. :contentReference[oaicite:42]{index=42}

---

## 10. What the Dispatching Objective Really Is

The slide deck states the formal objective simply:

- **Find the processing sequence to meet production goals of required date and move targets** :contentReference[oaicite:43]{index=43}

But the case makes clear that, in practice, the objective is broader. A good CMP dispatching policy must simultaneously:

- protect bottleneck CMP capacity,
- prevent queue-time violations,
- manage water tank occupancy,
- anticipate reconfiguration needs,
- preserve responsiveness for urgent lots,
- and reduce cycle time and excess WIP. :contentReference[oaicite:44]{index=44}

So the actual optimization target is a **multi-objective operational balance**, not just sequence optimization.

---

## 11. Distilled Design Principles for the Dispatching Algorithm

From the two documents, the following knowledge can be distilled as the design logic behind an effective CMP dispatching algorithm.

### Principle 1: Dispatch the Stage, Not the Tool
The sorter, CMP tool, water tank, and cleaner must be considered as one connected stage. Local optimization at the sorter can create global infeasibility downstream. :contentReference[oaicite:45]{index=45}

### Principle 2: Control Release Based on Downstream Feasibility
Lots should be released into CMP only when downstream cleaner route, water tank capacity, and queue-time feasibility are all acceptable. This is the essence of the move from **push** to **pull**. :contentReference[oaicite:46]{index=46}

### Principle 3: Protect Bottleneck Capacity First
Since CMP is the bottleneck, avoid starving or blocking it. A slightly suboptimal local priority choice may still be correct if it preserves CMP flow. :contentReference[oaicite:47]{index=47} :contentReference[oaicite:48]{index=48}

### Principle 4: Treat Intermediate Buffers as Strategic Resources
Water tanks are not passive storage. They are active control points that determine whether CMP can continue running. Their type assignment and occupancy should be planned explicitly. :contentReference[oaicite:49]{index=49}

### Principle 5: Include Changeovers in Near-Future Planning
Because tool and tank changeovers take from **0.5 hours to 6 hours**, dispatching cannot be purely myopic. It must anticipate load shifts before they become emergencies. :contentReference[oaicite:50]{index=50} :contentReference[oaicite:51]{index=51}

### Principle 6: Preserve Responsiveness Before Lots Become “Locked In”
Once lots pass the sorter, flexibility decreases. Therefore, urgency should be handled earlier, before lots enter a FIFO-like post-sort flow. :contentReference[oaicite:52]{index=52}

### Principle 7: Exploit Batch Synergy When Safe
Because CMP gains around **3 minutes per subsequent lot** under cascading/continuous processing, dispatching should exploit batching efficiencies where possible, but never at the expense of violating downstream time-window feasibility. :contentReference[oaicite:53]{index=53} :contentReference[oaicite:54]{index=54}

---

## 12. Push vs. Pull: The Strategic Shift

One of the most important conceptual contributions of the case is the shift from **push dispatching** to **pull dispatching**.

### Push Logic
- Release lots according to move targets or upstream availability
- Risks overloading constrained downstream resources
- Tends to create excess WIP, blocking, and longer cycle time :contentReference[oaicite:55]{index=55}

### Pull Logic
- Release lots based on real-time downstream consumption and system state
- Better aligns flow with actual cleaner and tank capacity
- Improves responsiveness and protects bottleneck utilization :contentReference[oaicite:56]{index=56}

This is not merely a scheduling tweak; it is a **control philosophy change**.

---

## 13. High-Level Knowledge Synthesis

### Core Insight
CMP dispatching is a **finite-buffer, time-window-constrained, multi-class, partially reconfigurable flow-control problem**.

### What makes it hard
It combines:
- bottleneck machines,
- serial batching,
- route-dependent cleaners,
- shared but partitioned water tanks,
- long changeovers,
- queue-time violations with rework/scrap consequences,
- and reduced lot distinguishability after sorting. :contentReference[oaicite:57]{index=57} :contentReference[oaicite:58]{index=58}

### What the algorithm must do
A strong algorithm must decide:
- **which lots to release,**
- **when to release them,**
- **to which downstream route,**
- **under what current and anticipated capacity state,**
so that the system remains feasible and productive over time. :contentReference[oaicite:59]{index=59}

### Final distilled takeaway
> In CMP, the best dispatching rule is not the one that simply prioritizes the most urgent lot; it is the one that keeps the entire constrained stage flowing while still protecting due dates and responsiveness. :contentReference[oaicite:60]{index=60} :contentReference[oaicite:61]{index=61}

---

## 14. One-Paragraph Conclusion

Taken together, the two documents show that CMP dispatching at SSMC is a classic example of why advanced manufacturing control must move beyond simple dispatch lists. The operational challenge comes from the interaction of queue-time limits, finite shared buffers, cleaner specialization, lengthy changeovers, and bottleneck protection. The central solution direction is a **pull-based, real-time, stage-level dispatching policy** that only releases work when downstream conditions are feasible and strategically desirable. This reframes dispatching from a local sequencing task into an integrated flow-control problem across the entire CMP stage. :contentReference[oaicite:62]{index=62} :contentReference[oaicite:63]{index=63}