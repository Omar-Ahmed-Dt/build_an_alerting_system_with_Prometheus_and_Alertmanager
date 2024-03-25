# How to build an alerting system with Prometheus and Alertmanager

**How Alertmanager works**
- The Prometheus server is a component that sends alerts to Alertmanager. Alertmanager is responsible for receiving, deduplicating, grouping, and routing alerts to various notification systems such as email, webhook, or other alerting systems via an API. Alertmanager also provides additional features such as silence management, notification inhibition, and alert template rendering.

<img src=imgs/alert-manager.png>

## Steps: 
**1- Web application exporter :**
- Our new exporter will be a simple web application built in the Python Flask framework
- We have a simple HTTP /up endpoint and also the /metrics endpoint

```
flask run --host=0.0.0.0 --port=8000
```

**2- Defining Dockerfile and Containerize the application :**

<img src=imgs/up.png>
<img src=imgs/metrics.png>

**3- Alerting rules :**
- define a Prometheus rules file

```
# rules.yml
groups:
  - name: web-app
    rules:
      - alert: Application down
        for: 1m
        expr: up{job="web-app"} == 0
        labels:
          severity: critical
        annotations:
          title: App is down on {{ $labels.instance }}
          description: The app on instance {{ $labels.instance }} has been down for the past 1 minute.
```

- To configure a rules file in Prometheus, we need to add its path to rule_files section in the prometheus.yml configuration file : 
```
# prometheus.yml

global:
  scrape_interval: 15s
rule_files:
  - "rules.yml"
alerting:
  alertmanagers:
    - static_configs:
        - targets: ["alertmanager:9093"]
scrape_configs:
  - job_name: "prometheus"
    scrape_interval: 5s
    static_configs:
      - targets: ["localhost:9090"]
  - job_name: "web-app"
    scrape_interval: 5s
    static_configs:
      - targets: ["web-app:8000"]
```

**5- Configure Slack and Notifications configuration:**
- Create Channel and its name is : < monitoring >

- Copy the webhook URL that you obtained in the Slack app installation process.

**5-  Alertmanager installation :**
- configuration to the route and receivers section in the alertmanager.yml : 
```
# alertmanager.yml

route:
  receiver: default
  routes:
    - matchers:
        - severity="critical"
      receiver: slack
receivers:
  - name: slack
    slack_configs:
      - channel: "#monitoring"
        send_resolved: true
        api_url: "https://hooks.slack.com/services/XXXXX"
        title: Alert
        text: >-
          {{ range .Alerts -}}
          *Alert:* {{ .Annotations.title }}{{ if .Labels.severity }} - `{{ .Labels.severity }}`{{ end }}
          *Description:* {{ .Annotations.description }}
          *Details:*
            {{ range .Labels.SortedPairs }} • *{{ .Name }}:* `{{ .Value }}`
            {{ end }}
          {{ end }}
  - name: default
```

**6- Configure and Start our Docker Compose stack :**

```
docker-compose up
```

## Testing : 
- We can now restart our Docker Compose stack and kill web-app instance again to trigger the "Application Down" alert. It should result in firing the alert and sending the following message on a given Slack channel: 

<img src=imgs/fire.png>
<img src=imgs/alert-fire.png>
<img src=imgs/fire-slack.png>