import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, precision_recall_curve,
    confusion_matrix, classification_report
)
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Tuple, Optional

class DeepfakeMetrics:
    """Comprehensive metrics for deepfake detection evaluation"""
    
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
    
    def compute_metrics(self, predictions: np.ndarray, 
                       labels: np.ndarray, 
                       threshold: Optional[float] = None) -> Dict[str, float]:
        """Compute comprehensive metrics"""
        if threshold is None:
            threshold = self.threshold
        
        # Convert predictions to binary
        binary_preds = (predictions >= threshold).astype(int)
        
        # Basic metrics
        accuracy = accuracy_score(labels, binary_preds)
        precision = precision_score(labels, binary_preds, zero_division=0)
        recall = recall_score(labels, binary_preds, zero_division=0)
        f1 = f1_score(labels, binary_preds, zero_division=0)
        
        # AUC metrics
        try:
            auc = roc_auc_score(labels, predictions)
        except ValueError:
            auc = 0.0
        
        # Additional metrics
        tn, fp, fn, tp = confusion_matrix(labels, binary_preds).ravel()
        
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        npv = tn / (tn + fn) if (tn + fn) > 0 else 0.0  # Negative Predictive Value
        
        # Balanced accuracy
        balanced_acc = (recall + specificity) / 2
        
        # Matthews Correlation Coefficient
        mcc_num = (tp * tn) - (fp * fn)
        mcc_den = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
        mcc = mcc_num / mcc_den if mcc_den > 0 else 0.0
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'auc': auc,
            'specificity': specificity,
            'npv': npv,
            'balanced_accuracy': balanced_acc,
            'mcc': mcc,
            'true_positives': int(tp),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn)
        }
    
    def find_optimal_threshold(self, predictions: np.ndarray, 
                              labels: np.ndarray) -> Tuple[float, Dict[str, float]]:
        """Find optimal threshold using Youden's J statistic"""
        fpr, tpr, thresholds = roc_curve(labels, predictions)
        
        # Youden's J statistic
        j_scores = tpr - fpr
        optimal_idx = np.argmax(j_scores)
        optimal_threshold = thresholds[optimal_idx]
        
        # Compute metrics at optimal threshold
        optimal_metrics = self.compute_metrics(predictions, labels, optimal_threshold)
        
        return optimal_threshold, optimal_metrics
    
    def plot_roc_curve(self, predictions: np.ndarray, 
                       labels: np.ndarray, 
                       save_path: Optional[str] = None) -> plt.Figure:
        """Plot ROC curve"""
        fpr, tpr, _ = roc_curve(labels, predictions)
        auc = roc_auc_score(labels, predictions)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(fpr, tpr, linewidth=2, label=f'ROC Curve (AUC = {auc:.3f})')
        ax.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random')
        
        ax.set_xlabel('False Positive Rate')
        ax.set_ylabel('True Positive Rate')
        ax.set_title('ROC Curve - Deepfake Detection')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_precision_recall_curve(self, predictions: np.ndarray, 
                                   labels: np.ndarray,
                                   save_path: Optional[str] = None) -> plt.Figure:
        """Plot Precision-Recall curve"""
        precision, recall, _ = precision_recall_curve(labels, predictions)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(recall, precision, linewidth=2, label='PR Curve')
        
        ax.set_xlabel('Recall')
        ax.set_ylabel('Precision')
        ax.set_title('Precision-Recall Curve - Deepfake Detection')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_confusion_matrix(self, predictions: np.ndarray, 
                             labels: np.ndarray,
                             threshold: Optional[float] = None,
                             save_path: Optional[str] = None) -> plt.Figure:
        """Plot confusion matrix"""
        if threshold is None:
            threshold = self.threshold
        
        binary_preds = (predictions >= threshold).astype(int)
        cm = confusion_matrix(labels, binary_preds)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                   xticklabels=['Real', 'Fake'],
                   yticklabels=['Real', 'Fake'])
        
        ax.set_xlabel('Predicted')
        ax.set_ylabel('Actual')
        ax.set_title(f'Confusion Matrix (Threshold = {threshold:.3f})')
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def generate_classification_report(self, predictions: np.ndarray, 
                                     labels: np.ndarray,
                                     threshold: Optional[float] = None) -> str:
        """Generate detailed classification report"""
        if threshold is None:
            threshold = self.threshold
        
        binary_preds = (predictions >= threshold).astype(int)
        
        report = classification_report(
            labels, binary_preds,
            target_names=['Real', 'Fake'],
            digits=4
        )
        
        return report
    
    def evaluate_model_comprehensive(self, predictions: np.ndarray, 
                                   labels: np.ndarray,
                                   save_dir: Optional[str] = None) -> Dict:
        """Comprehensive model evaluation"""
        # Find optimal threshold
        optimal_threshold, optimal_metrics = self.find_optimal_threshold(predictions, labels)
        
        # Compute metrics at default threshold
        default_metrics = self.compute_metrics(predictions, labels)
        
        # Generate plots
        if save_dir:
            import os
            os.makedirs(save_dir, exist_ok=True)
            
            self.plot_roc_curve(predictions, labels, 
                               os.path.join(save_dir, 'roc_curve.png'))
            self.plot_precision_recall_curve(predictions, labels,
                                            os.path.join(save_dir, 'pr_curve.png'))
            self.plot_confusion_matrix(predictions, labels, optimal_threshold,
                                     os.path.join(save_dir, 'confusion_matrix.png'))
        
        # Classification report
        classification_rep = self.generate_classification_report(predictions, labels, optimal_threshold)
        
        return {
            'optimal_threshold': optimal_threshold,
            'optimal_metrics': optimal_metrics,
            'default_metrics': default_metrics,
            'classification_report': classification_rep
        }
