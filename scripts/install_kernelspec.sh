# Register the kernel
$QUARTO_PYTHON -m ipykernel install --user --name learning-portal --display-name "Learning Portal"

# Verify kernel installation
jupyter kernelspec list

echo "Kernel installation complete!"
