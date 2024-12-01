/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2024 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#define ARM_MATH_CM4
#include "arm_math.h"
#include <math.h>
#include <stdio.h>
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
#define SIZE_BUFFER 320
#define SAMPLE_RATE 8000
#define DURATION 0.25 // 250 milliseconds
#define NUM_SAMPLES 2000


int current_position;
int calibrationDone;

// calibration values
int16_t accelero_p0[3] = {0,0,0};
int16_t accelero_p1[3] = {0,0,0};
int16_t accelero_p2[3] = {0,0,0};
int16_t accelero_p3[3] = {0,0,0};

int16_t accelero[3] = {0,0,0};

// Calibration offsets
float OFFX = 0.0f;
float OFFY = 0.0f;

// Sensitivity values
float SENSX = 0.0f;
float SENSY = 0.0f;

// Constants
float CXY = 0.0f;
float CYX = 0.0f;

float ACCX = 0.0f;
float ACCY = 0.0f;
float ACCX_prime = 0.0f;
float ACCY_prime = 0.0f;

// Game Over sound
HAL_StatusTypeDef STATUS;
uint8_t sine_g4[112];
uint8_t sine_e4[134];
uint8_t sine_c4[169];

uint8_t *current_tone = sine_g4;
int current_num_sample = 112;
int tone_index = 0;
int periods = 0;
int tone = 0;
int start = 1;

uint8_t rxBuffer[100];
HAL_StatusTypeDef rxStatus;

char txBuffer[SIZE_BUFFER];
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
DAC_HandleTypeDef hdac1;

I2C_HandleTypeDef hi2c2;

TIM_HandleTypeDef htim2;

UART_HandleTypeDef huart1;

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_USART1_UART_Init(void);
static void MX_I2C2_Init(void);
static void MX_DAC1_Init(void);
static void MX_TIM2_Init(void);
/* USER CODE BEGIN PFP */
volatile int button_pressed = 0;  // Global flag to track button press
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

void generate_gameover_sound_waves(){
	//G4 : 392 Hz
	for (int j = 0; j < 112; j++){
		 sine_g4[j] = (uint8_t)((arm_sin_f32((2*M_PI/112)*j)+1)*20470.5f);
	}
	//E4: 330 Hz
	for (int j=0; j < 134; j++) {
		sine_e4[j] = (uint8_t)((arm_sin_f32((2*M_PI/134)*j)+1)*2047.5f);
	}
	//C4: 261.63 Hz
	for (int j = 0; j < 169; j++){
		 sine_c4[j] = (uint8_t)((arm_sin_f32((2*M_PI/169)*j)+1)*2047.5f);
	}
}

void play_gameover_sound(){
	start = 0;
	current_tone = sine_g4;
	current_num_sample = 112;
	tone_index = 0;

	HAL_TIM_Base_Start_IT(&htim2);
}

void play_start_sound(){
	start = 1;
	current_tone = sine_c4;
	current_num_sample = 169;
	tone_index = 0;

	HAL_TIM_Base_Start_IT(&htim2);
}

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    if (GPIO_Pin == myButton_Pin) {
        printf("Button Pressed! Current Position: %d\r\n", current_position);

        // Record accelerometer data
        if (current_position == 0) {
            BSP_ACCELERO_AccGetXYZ(accelero_p0);
        } else if (current_position == 1) {
            BSP_ACCELERO_AccGetXYZ(accelero_p1);
        } else if (current_position == 2) {
            BSP_ACCELERO_AccGetXYZ(accelero_p2);
        } else if (current_position == 3) {
            BSP_ACCELERO_AccGetXYZ(accelero_p3);
        }


	        current_position++;

	        if (current_position > 3) {
	            calibrationDone = 1;
	            printf("Calibration complete!\r\n");
	        }
	    }

	if(calibrationDone) {
//		if(GPIO_Pin == myButton_Pin) {
//			buttonStatus_after_Calibration = 1;
////			printf("Button Pressed! Shoot!", current_position);
//		}
//		else{
//			buttonStatus_after_Calibration = 0;
//		}
	    if (GPIO_Pin == myButton_Pin) {
	        button_pressed = 1;  // Set flag on button press
	    }
	}
}

void calibrate_accelerometer() {
	  // Compute offsets
	  OFFX = (accelero_p0[0] + accelero_p1[0] + accelero_p2[0] + accelero_p3[0]) / 4;
	  OFFY = (accelero_p0[1] + accelero_p1[1] + accelero_p2[1] + accelero_p3[1]) / 4;

	  // Compute sensitivities
	  SENSX = (accelero_p2[0] - accelero_p1[0]) / 2;
	  SENSY = (accelero_p0[1] - accelero_p3[1]) / 2;

	  // Compute calibration factors
	  CXY = (accelero_p0[0] - accelero_p3[0]) / (2 * SENSX);
	  CYX = (accelero_p2[1] - accelero_p1[1]) / (2 * SENSY);
}

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */

	//char output[SIZE_BUFFER];

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_USART1_UART_Init();
  MX_I2C2_Init();
  MX_DAC1_Init();
  MX_TIM2_Init();
  /* USER CODE BEGIN 2 */
  BSP_ACCELERO_Init();
  //BSP_GYRO_Init();

  HAL_UART_Init(&huart1);
  rxStatus = HAL_UART_Receive_IT(&huart1, rxBuffer, 10);

  current_position = 0;
  calibrationDone = 0;

  while (calibrationDone == 0) {
	  // waiting loop
	  sprintf(txBuffer, "Waiting for calibration \r\n");

	  HAL_UART_Transmit(&huart1, (uint8_t *)txBuffer, SIZE_BUFFER, 100);
	  HAL_Delay(1000);

	  for(int i = 0; i < SIZE_BUFFER; i++) {
		  txBuffer[i] = 0;
	  }
  }

  calibrate_accelerometer();
  sprintf(txBuffer, "Calibration done \r\n");
  HAL_UART_Transmit(&huart1, (uint8_t *)txBuffer, SIZE_BUFFER, 100);
  HAL_Delay(1000);

  for(int i = 0; i < SIZE_BUFFER; i++) {
	  txBuffer[i] = 0;
  }

  generate_gameover_sound_waves();

  STATUS = HAL_DAC_Start(&hdac1, DAC_CHANNEL_1);
  	if(STATUS!=HAL_OK){
  	  Error_Handler();
  	}

  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  play_start_sound();





  while (1)
  {
	  //rxStatus = HAL_UART_Receive_IT(&huart1, rxBuffer, 100);
	  int temp = 0;
	    if (button_pressed) {
	        // Reset the flag
	        button_pressed = 0;
	        temp = 1;

	    }


	  BSP_ACCELERO_AccGetXYZ(accelero);

	  // Initial estimates
	  ACCX_prime = (accelero[0] - OFFX) / SENSX;
	  ACCY_prime = (accelero[1] - OFFY) / SENSY;

	  // Iterative process
	  //for (int i = 0; i < 10; i++) {
		// Update ACCX' and ACCY' values
	//	ACCX_prime = (accelero[0] - OFFX) / SENSX - ACCY_prime * CXY;
	//	ACCY_prime = (accelero[1] - OFFY) / SENSY - ACCX_prime * CYX;
	  //}

	  // Store final calibrated values
	  ACCX = ACCX_prime;
	  ACCY = ACCY_prime;

	  // Compute tilt angle in radians
	  float tilt = atan2f(ACCX, sqrtf(ACCY * ACCY));

	  // Convert radians to degrees if needed
	  float tilt_degrees = tilt * 180 / PI;


	  sprintf(txBuffer, "Calibrated Accelero X: %f, Y: %f, Tilt degrees: %f, Shoot: %d \r\n", ACCX, ACCY, tilt_degrees, temp);
	  temp = 0;
//	  sprintf(output, "Accelero X: %d, Y: %d, Z: %d \r\n", accelero[0], accelero[1], accelero[2]);
	  HAL_Delay(5);
	  HAL_UART_Transmit(&huart1, (uint8_t *)txBuffer, SIZE_BUFFER,100);
	  HAL_Delay(5);
	  for(int i = 0; i < SIZE_BUFFER; i++) {
	       txBuffer[i] = 0;
	  }

    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }


  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  if (HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE1_BOOST) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_MSI;
  RCC_OscInitStruct.MSIState = RCC_MSI_ON;
  RCC_OscInitStruct.MSICalibrationValue = 0;
  RCC_OscInitStruct.MSIClockRange = RCC_MSIRANGE_6;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_MSI;
  RCC_OscInitStruct.PLL.PLLM = 1;
  RCC_OscInitStruct.PLL.PLLN = 60;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = RCC_PLLQ_DIV2;
  RCC_OscInitStruct.PLL.PLLR = RCC_PLLR_DIV2;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_5) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief DAC1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_DAC1_Init(void)
{

  /* USER CODE BEGIN DAC1_Init 0 */

  /* USER CODE END DAC1_Init 0 */

  DAC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN DAC1_Init 1 */

  /* USER CODE END DAC1_Init 1 */

  /** DAC Initialization
  */
  hdac1.Instance = DAC1;
  if (HAL_DAC_Init(&hdac1) != HAL_OK)
  {
    Error_Handler();
  }

  /** DAC channel OUT1 config
  */
  sConfig.DAC_SampleAndHold = DAC_SAMPLEANDHOLD_DISABLE;
  sConfig.DAC_Trigger = DAC_TRIGGER_NONE;
  sConfig.DAC_HighFrequency = DAC_HIGH_FREQUENCY_INTERFACE_MODE_ABOVE_80MHZ;
  sConfig.DAC_OutputBuffer = DAC_OUTPUTBUFFER_ENABLE;
  sConfig.DAC_ConnectOnChipPeripheral = DAC_CHIPCONNECT_DISABLE;
  sConfig.DAC_UserTrimming = DAC_TRIMMING_FACTORY;
  if (HAL_DAC_ConfigChannel(&hdac1, &sConfig, DAC_CHANNEL_1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN DAC1_Init 2 */

  /* USER CODE END DAC1_Init 2 */

}

/**
  * @brief I2C2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_I2C2_Init(void)
{

  /* USER CODE BEGIN I2C2_Init 0 */

  /* USER CODE END I2C2_Init 0 */

  /* USER CODE BEGIN I2C2_Init 1 */

  /* USER CODE END I2C2_Init 1 */
  hi2c2.Instance = I2C2;
  hi2c2.Init.Timing = 0x307075B1;
  hi2c2.Init.OwnAddress1 = 0;
  hi2c2.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
  hi2c2.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
  hi2c2.Init.OwnAddress2 = 0;
  hi2c2.Init.OwnAddress2Masks = I2C_OA2_NOMASK;
  hi2c2.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
  hi2c2.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
  if (HAL_I2C_Init(&hi2c2) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Analogue filter
  */
  if (HAL_I2CEx_ConfigAnalogFilter(&hi2c2, I2C_ANALOGFILTER_ENABLE) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Digital filter
  */
  if (HAL_I2CEx_ConfigDigitalFilter(&hi2c2, 0) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN I2C2_Init 2 */

  /* USER CODE END I2C2_Init 2 */

}

/**
  * @brief TIM2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM2_Init(void)
{

  /* USER CODE BEGIN TIM2_Init 0 */

  /* USER CODE END TIM2_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM2_Init 1 */

  /* USER CODE END TIM2_Init 1 */
  htim2.Instance = TIM2;
  htim2.Init.Prescaler = 0;
  htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim2.Init.Period = 2721;
  htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_Base_Init(&htim2) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim2, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim2, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM2_Init 2 */

  /* USER CODE END TIM2_Init 2 */

}

/**
  * @brief USART1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART1_UART_Init(void)
{

  /* USER CODE BEGIN USART1_Init 0 */

  /* USER CODE END USART1_Init 0 */

  /* USER CODE BEGIN USART1_Init 1 */

  /* USER CODE END USART1_Init 1 */
  huart1.Instance = USART1;
  huart1.Init.BaudRate = 115200;
  huart1.Init.WordLength = UART_WORDLENGTH_8B;
  huart1.Init.StopBits = UART_STOPBITS_1;
  huart1.Init.Parity = UART_PARITY_NONE;
  huart1.Init.Mode = UART_MODE_TX_RX;
  huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart1.Init.OverSampling = UART_OVERSAMPLING_16;
  huart1.Init.OneBitSampling = UART_ONE_BIT_SAMPLE_DISABLE;
  huart1.Init.ClockPrescaler = UART_PRESCALER_DIV1;
  huart1.AdvancedInit.AdvFeatureInit = UART_ADVFEATURE_NO_INIT;
  if (HAL_UART_Init(&huart1) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_UARTEx_SetTxFifoThreshold(&huart1, UART_TXFIFO_THRESHOLD_1_8) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_UARTEx_SetRxFifoThreshold(&huart1, UART_RXFIFO_THRESHOLD_1_8) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_UARTEx_DisableFifoMode(&huart1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART1_Init 2 */

  /* USER CODE END USART1_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
/* USER CODE BEGIN MX_GPIO_Init_1 */
/* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin : myButton_Pin */
  GPIO_InitStruct.Pin = myButton_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(myButton_GPIO_Port, &GPIO_InitStruct);

  /* EXTI interrupt init*/
  HAL_NVIC_SetPriority(EXTI15_10_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(EXTI15_10_IRQn);

/* USER CODE BEGIN MX_GPIO_Init_2 */
/* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
	if (htim->Instance == TIM2) {
		HAL_IncTick();
		if(periods<80){
			STATUS = HAL_DAC_SetValue(&hdac1, DAC_CHANNEL_1, DAC_ALIGN_12B_R, current_tone[tone_index++]);
			if(STATUS != HAL_OK){
				Error_Handler();
			}
			if(tone_index==current_num_sample){
				tone_index=0;
				periods++;
			}
		}
		else {
			tone++;
			tone_index=0;
			periods = 0;

			switch(tone){
				case 1:
					current_tone = sine_e4;
					current_num_sample = 134;
					break;
				case 2:
					if(start){
						current_tone = sine_g4;
						current_num_sample = 112;
					}else {
						current_tone = sine_c4;
						current_num_sample = 169;
					}
					break;
				default:
					HAL_TIM_Base_Stop_IT(&htim2);
					tone = 0;
					return;
			}


		}
	}
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
  if (huart->Instance == USART1)
  {
    HAL_UART_Receive_IT(&huart1, rxBuffer, 10);

    if (strstr((char *)rxBuffer, "GAME_OVER\n") != NULL) {
      play_gameover_sound();
      memset(rxBuffer, 0, sizeof(rxBuffer));
    }
  }
}


/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
