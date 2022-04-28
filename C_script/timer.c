/*
 * timer.c
 *
 *  Created on: 20 feb 2022
 *      Author: Alessio
 */
#include <msp430.h>
unsigned long milliseconds;




void init_timer(void)
{
    milliseconds = 0;
    TA0CTL = TASSEL_2;//seleziona la fonte del clock
    TA0CTL &= ~ TAIFG;
    TA0CCR0 = 1000;  // periodo del timer (1mS)
    TA0CTL |= MC_1 + TACLR;  //in up mode
    TA0CTL |= TAIE; //abilita interrupt timer
   __enable_interrupt();
}

unsigned long millis(void)
{
 unsigned long retval;
 TA1CTL &=~TAIE; //disabilita interrupt timer
 retval = milliseconds; //legge il valore del contatore
 TA1CTL |=TAIE; //abilita interrupt timer
 return retval;  //ritorna il valore
 }


#pragma vector = TIMER0_A1_VECTOR
 __interrupt void isr_timer(void)
 {
     milliseconds++; //contatore
     TA0CTL &= ~ TAIFG; //reset taifg flag
 }
