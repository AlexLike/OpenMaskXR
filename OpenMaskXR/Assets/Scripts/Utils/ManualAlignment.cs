using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.XR;

[RequireComponent(typeof(MeshRenderer))]
public class ManualAlignment : MonoBehaviour
{
    // Input actions
    public InputActionReference leftPrimaryButtonAction;
    public InputActionReference rightPrimaryButtonAction;
    public InputActionReference leftJoystickAction;
    public InputActionReference rightJoystickAction;

    private MeshRenderer meshRenderer;
    private bool isActive = false;

    // Timer for button holding
    private float buttonHoldTime = 0f;
    private bool buttonsHeld = false;
    private const float activationTime = 3f;

    // Movement and rotation acceleration variables
    [Header("Speed Settings")]
    private float movementSpeed = 0f;
    private float rotationSpeed = 0f;
    [SerializeField] private const float maxMovementSpeed = 3f;
    [SerializeField] private const float maxRotationSpeed = 45f; // degrees per second
    [SerializeField] private const float accelerationRate = 2f;
    [SerializeField] private const float decelerationRate = 10f;

    void Start()
    {
        meshRenderer = GetComponent<MeshRenderer>();
        if (meshRenderer != null)
            meshRenderer.enabled = false;
    }

    void Update()
    {
        // Check if both primary buttons are held down
        bool leftButtonPressed = leftPrimaryButtonAction.action.IsPressed();
        bool rightButtonPressed = rightPrimaryButtonAction.action.IsPressed();

        if (leftButtonPressed && rightButtonPressed)
        {
            buttonHoldTime += Time.deltaTime;
            if (buttonHoldTime >= activationTime && !buttonsHeld)
            {
                ToggleControl();
                buttonsHeld = true;
            }
        }
        else
        {
            buttonHoldTime = 0f;
            buttonsHeld = false;
        }

        // Handle movement and rotation if active
        if (isActive)
        {
            HandleMovement();
        }
    }

    private void ToggleControl()
    {
        isActive = !isActive;
        if (meshRenderer != null)
            meshRenderer.enabled = isActive;
    }

    private void HandleMovement()
    {
        // Read joystick values
        Vector2 leftJoystick = leftJoystickAction.action.ReadValue<Vector2>();
        Vector2 rightJoystick = rightJoystickAction.action.ReadValue<Vector2>();

        // Handle movement with acceleration
        if (leftJoystick.magnitude > 0.1f)
        {
            movementSpeed = Mathf.Min(movementSpeed + accelerationRate * Time.deltaTime, maxMovementSpeed);
            Vector3 movement = new Vector3(leftJoystick.x, 0, leftJoystick.y) * movementSpeed * Time.deltaTime;
            transform.Translate(movement, Space.World);
        }
        else
        {
            // Decelerate when joystick is released
            movementSpeed = Mathf.Max(movementSpeed - decelerationRate * Time.deltaTime, 0f);
        }

        // Handle rotation with acceleration
        if (Mathf.Abs(rightJoystick.x) > 0.1f)
        {
            rotationSpeed = Mathf.Min(rotationSpeed + accelerationRate * 10 * Time.deltaTime, maxRotationSpeed);
            float rotationAmount = rightJoystick.x * rotationSpeed * Time.deltaTime;
            transform.Rotate(Vector3.up, rotationAmount);
        }
        else
        {
            // Decelerate rotation when joystick is released
            rotationSpeed = Mathf.Max(rotationSpeed - decelerationRate * 10 * Time.deltaTime, 0f);
        }
    }
}