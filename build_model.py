"""Build entry point: evaluate all baselines and save the training-only forest."""
from evaluate_model import run
run()
print('Grouped holdout evaluation complete; training-only Random Forest saved for deployment.')
