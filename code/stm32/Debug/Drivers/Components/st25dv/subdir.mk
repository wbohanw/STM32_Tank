################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (12.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../Drivers/Components/st25dv/st25dv.c \
../Drivers/Components/st25dv/st25dv_reg.c 

OBJS += \
./Drivers/Components/st25dv/st25dv.o \
./Drivers/Components/st25dv/st25dv_reg.o 

C_DEPS += \
./Drivers/Components/st25dv/st25dv.d \
./Drivers/Components/st25dv/st25dv_reg.d 


# Each subdirectory must supply rules for building sources it contributes
Drivers/Components/st25dv/%.o Drivers/Components/st25dv/%.su Drivers/Components/st25dv/%.cyclo: ../Drivers/Components/st25dv/%.c Drivers/Components/st25dv/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32L4S5xx -c -I../Core/Inc -I"/Users/bohan/Desktop/McGill_ECSE444/code/stm32/Drivers/Components/hts221" -I"/Users/bohan/Desktop/McGill_ECSE444/code/stm32/Drivers/Components" -I../Drivers/STM32L4xx_HAL_Driver/Inc -I../Drivers/STM32L4xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32L4xx/Include -I../Drivers/CMSIS/Include -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-Drivers-2f-Components-2f-st25dv

clean-Drivers-2f-Components-2f-st25dv:
	-$(RM) ./Drivers/Components/st25dv/st25dv.cyclo ./Drivers/Components/st25dv/st25dv.d ./Drivers/Components/st25dv/st25dv.o ./Drivers/Components/st25dv/st25dv.su ./Drivers/Components/st25dv/st25dv_reg.cyclo ./Drivers/Components/st25dv/st25dv_reg.d ./Drivers/Components/st25dv/st25dv_reg.o ./Drivers/Components/st25dv/st25dv_reg.su

.PHONY: clean-Drivers-2f-Components-2f-st25dv

