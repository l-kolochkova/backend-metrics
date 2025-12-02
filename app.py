"""Example of flask main file with Prometheus metrics."""
from flask import Flask, Response
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Gauge, generate_latest, REGISTRY
import psutil
import os

app = Flask(__name__)

# Initialize PrometheusMetrics but disable default metrics endpoint
metrics = PrometheusMetrics(app, path=None)

# Create custom gauge for memory usage with the specified naming convention
app_memory_usage_gauge = Gauge(
    'app_memory_usage_v20kijyl',
    'Application memory usage in bytes',
    ['type']  # Label to distinguish between different memory types
)

def update_memory_metrics():
    """Update memory metrics with current values."""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    # Update different memory metrics
    app_memory_usage_gauge.labels(type='rss').set(memory_info.rss)  # Resident Set Size
    app_memory_usage_gauge.labels(type='vms').set(memory_info.vms)  # Virtual Memory Size
    
    # Get memory percentage
    memory_percent = process.memory_percent()
    app_memory_usage_gauge.labels(type='percent').set(memory_percent)


@app.route('/api/hello')
def hello_world():
    """Returns Hello, EDP!"""
    return 'Hello, EDP!'


@app.route('/actuator/prometheus')
def prometheus_metrics():
    """Expose metrics at /actuator/prometheus endpoint."""
    # Update memory metrics before serving
    update_memory_metrics()
    
    # Generate latest metrics in Prometheus format
    return Response(generate_latest(REGISTRY), mimetype='text/plain')


@app.before_request
def before_request():
    """Update metrics before each request."""
    update_memory_metrics()


if __name__ == '__main__':
    app.run()