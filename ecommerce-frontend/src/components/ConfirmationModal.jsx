import React from 'react';
import { Modal, Button } from 'react-bootstrap';

/**
 * ConfirmationModal Component
 * A reusable modal component to confirm critical actions (e.g., deletions, updates).
 *
 * Props:
 * - show: Boolean to control modal visibility.
 * - message: The confirmation message to display.
 * - onConfirm: Function to call when the action is confirmed.
 * - onCancel: Function to call when the action is canceled.
 */
const ConfirmationModal = ({ show, message, onConfirm, onCancel }) => {
  return (
    <Modal show={show} onHide={onCancel} centered>
      <Modal.Header closeButton>
        <Modal.Title>Confirm Action</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <p>{message}</p>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
        <Button variant="danger" onClick={onConfirm}>
          Confirm
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ConfirmationModal;
