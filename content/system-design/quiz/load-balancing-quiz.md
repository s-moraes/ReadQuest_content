## Q1
Which load balancing algorithm selects servers strictly in sequential cyclical order?

### Option A [CORRECT]
Round Robin

### Option B
Least Connections

### Option C
IP Hash

### Option D
Weighted Response Time

### Explanation
Round Robin rotates sequentially through the list of available healthy servers.
===
## Q2
When should you use Least Connections load balancing instead of Round Robin?

### Option A [CORRECT]
When requests have varying processing times or long-lived persistent connections.

### Option B
When all backend instances have identical CPU power and request times.

### Option C
Only when using UDP traffic.

### Option D
When no health checks are available.

### Explanation
Least Connections directs traffic to whichever server has the fewest active requests, ideal for uneven workloads.
===
## Q3
What is the primary benefit of L7 (Layer 7) load balancing over L4 (Layer 4)?

### Option A [CORRECT]
Content-based routing based on HTTP headers, URLs, and cookies.

### Option B
Lower CPU overhead on the balancer.

### Option C
Zero latency packet forwarding.

### Option D
Supports arbitrary binary protocols without inspection.

### Explanation
Layer 7 balancers inspect application-layer payloads (like HTTP paths or headers) to route intelligently.
===
## Q4
What happens when a load balancer's health check fails for an instance?

### Option A [CORRECT]
The unhealthy instance is removed from the rotation until checks pass again.

### Option B
All traffic to the cluster is terminated immediately.

### Option C
The instance is rebooted automatically by the balancer.

### Option D
Traffic to that instance is doubled to clear the backlog.

### Explanation
Health checks protect overall availability by dropping failing instances from active traffic.
