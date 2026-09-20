#!/bin/bash

###############################################################################
# Adaptive Conversational Risk Intake (ACRI)
# Code Ocean Execution Script
# Michael Aaron Russell, Universal Standard Axiom Corporation
###############################################################################

set -e  # Exit on error

echo "=========================================="
echo "ACRI - Adaptive Conversational Risk Intake"
echo "Code Ocean Deployment"
echo "=========================================="
echo ""

# Create results directory if it doesn't exist
mkdir -p /results

# Set working directory
cd /code

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

echo "Python version:"
python3 --version
echo ""

# Display configuration
echo "Configuration:"
cat /config/default_config.json | head -20
echo "..."
echo ""

# Run ACRI with sample application
echo "Executing ACRI underwriting process..."
echo ""

python3 acri_runner.py \
    --config /config/default_config.json \
    --application APP-20260919-001 \
    --data /data/sample_application.json

RESULT=$?

echo ""
echo "=========================================="
echo "Execution Complete"
echo "=========================================="
echo ""

# Check for results
if [ -f "/results/APP-20260919-001_results.json" ]; then
    echo "✓ Results successfully saved to /results/"
    echo ""
    echo "Output files:"
    ls -lh /results/
    echo ""
    echo "Summary of results:"
    python3 -m json.tool /results/APP-20260919-001_results.json | head -30
else
    echo "✗ Error: Results file not found"
    exit 1
fi

echo ""
echo "To run with custom data, use:"
echo "  python3 /code/acri_runner.py --config /config/default_config.json \\"
echo "    --application <APP_ID> --data <DATA_FILE>"
echo ""

exit $RESULT
