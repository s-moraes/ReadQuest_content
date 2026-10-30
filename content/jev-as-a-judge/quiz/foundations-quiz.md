## Q1
What is the primary bottleneck when using traditional generative Large Language Models as automated judges in real-time production systems?

### Option A
Generative judges cannot read JSON input prompts.

### Option B [CORRECT]
Generating multi-step Chain-of-Thought prose introduces multi-second latency and prohibitive token costs.

### Option C
Generative models can only execute binary classifications.

### Option D
Generative judges are incapable of running on modern cloud GPU hardware.

### Explanation
Traditional generative judges decode hundreds of tokens of step-by-step reasoning sequentially before outputting a verdict. This autoregressive decoding loop incurs multi-second latency (3,000–10,000ms) and costs thousands of dollars daily at web scale, making inline production evaluation unviable.

===

## Q2
How does a decision-only evaluator like TypeSafe JEV derive its verdict without running an autoregressive decoding loop?

### Option A
By executing an external regex search across the input prompt string.

### Option B
By compiling the prompt into a C++ binary.

### Option C [CORRECT]
By executing a single forward pass and extracting softmax probabilities directly from the logits of target decision tokens.

### Option D
By training a random forest classifier completely outside the neural network.

### Explanation
Decision-only evaluators bypass text generation entirely. The model processes the prompt in a single forward pass, and the system inspects the unnormalized logit values at the vocabulary head corresponding to target labels (such as "Yes" vs. "No" or "A" vs. "B") to compute decision probabilities.

===

## Q3
What does the Verbosity Bias refer to in generative LLM judges?

### Option A
The tendency of models to refuse to evaluate short responses.

### Option B [CORRECT]
The systemic tendency of judges to assign higher scores to longer, wordier answers even when they contain fluff or inaccuracies.

### Option C
The failure of models to generate text when memory buffers fill.

### Option D
The preference of models for responses written strictly in uppercase letters.

### Explanation
Verbosity bias is a documented cognitive flaw where evaluators favor longer, more detailed-looking responses over concise, accurate ones, because pre-training RLHF reward models correlate length and formatting with thoroughness.

===

## Q4
What characterizes a probabilistic evaluator that is "perfectly calibrated"?

### Option A
It predicts every single test sample with exactly 100% confidence.

### Option B
It never requires human feedback during production operations.

### Option C [CORRECT]
Its predicted probability matches the empirical accuracy: among predictions made with confidence p, exactly p fraction are correct.

### Option D
It maintains zero latency regardless of input token length.

### Explanation
Probability calibration means that confidence reflects true statistical likelihood. If a well-calibrated model assigns a confidence of 0.85 to 100 claims, exactly 85 of those claims will be empirically accurate.

===

## Q5
What is the effect of applying Temperature Scaling to a neural network's decision logits?

### Option A
It retrains all model weights via backpropagation.

### Option B
It changes the predicted class label to the second-highest logit.

### Option C
It permanently deletes unselected vocabulary tokens from memory.

### Option D [CORRECT]
It adjusts the confidence magnitude of the softmax distribution without altering the predicted argmax class label.

### Explanation
Temperature scaling divides all logits by a learned positive scalar T. Because dividing by a constant preserves the relative ordering of values, the predicted class label (argmax) remains identical, but overconfidence is softened to match empirical accuracy.
