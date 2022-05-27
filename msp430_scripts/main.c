#include <msp430.h>
#include <timer.h>
#include <stdio.h>

#define CALADC12_15V_30C *((unsigned int *)0x1A1A)
#define CALADC12_15V_85C *((unsigned int *)0x1A1C)
#define DELAY 120000

long int time;
char out[10] = {'z','z','z','z','z','z','z','z','z'};
unsigned int index=0;

void setup_adc();
void init_serial(void);

int main(void)
{
    WDTCTL = WDTPW | WDTHOLD;   // stop watchdog timer
    init_timer();               //turn on timer
    init_serial();              //turn on serial
    setup_adc();
    time = millis();
    while(1){


        if(millis() - time >= DELAY){   // ogni 2 minuti
            time = millis();
            ADC12CTL0 |= ADC12ENC + ADC12SC; //inizia conversione
            while(ADC12CTL1 & ADC12BUSY); //aspetta la fine della conversione

            int T = ((( (float) ( (long) ADC12MEM0 - CALADC12_15V_30C)*(55)) / (CALADC12_15V_85C - CALADC12_15V_30C)) + 30.0f) *10;

            int intera = T /10;
            int decimale = T % 10;

            sprintf(out,"%d.%d",intera,decimale);

            UCA1IE |= UCTXIE;

        }

    }
}


void setup_adc()
{
    REFCTL0 &= ~REFMSTR;
    ADC12CTL0 |= ADC12SHT0_8 + ADC12ON;

    ADC12CTL1 = ADC12SHP + ADC12CONSEQ_0;

    ADC12MCTL0 |= ADC12INCH_10;


    ADC12CTL0 |= ADC12REFON;
    ADC12CTL0 &= ~ADC12REF2_5V;
    ADC12MCTL0 |= ADC12SREF_1;
    ADC12CTL0 |= ADC12ENC + ADC12SC;

    while(ADC12CTL1 & ADC12BUSY); //attendi il termine della conversione
}


void init_serial(void)
{

    P4SEL |= BIT5 + BIT4;//setta bit 4 e 5 di P4sel (funzione speciale e non i/o) collega con usb

    UCA1CTL1 |= UCSWRST;   //apre la seriale in scrittura resetta seriale
    UCA1CTL1 |= UCSSEL_2;   //seleziona SMCLK come clock (circa 1MHZ)

    //impostazione baud rate
    UCA1BR0 = 109;   //imposta la velocità di 9600baud valore basso del prescaler
    UCA1BR1 = 0; //valore alto del prescaler
    UCA1MCTL = UCBRS_2; //modulazione (2°,3° BIT)

    UCA1CTL1 &= ~UCSWRST; //abilita seriale (abbassa il bit)
    //UCA1IE |= UCTXIE;
    //UCA1IE |= UCRXIE;
    //opzionale :
    //UCA1IE |= UCTXIE;     //nel registro interrupt  abilita interrupt trasmissione
    //UCA1IE |= UCRXIE;  // nel registro interrupt abilita interrupt in ricezione
    __enable_interrupt();
}

//UCA1IE &= ~UCTXIE;

#pragma vector=USCI_A1_VECTOR    // timer che utilizziamo = TIMER0
__interrupt void Interrupt(void)
{

    if(UCA1IFG & UCTXIFG){
        if( out[index] == '\0' ){
            UCA1IE &= ~UCTXIE;
            index = 0;
        }
        else
        {
            UCA1TXBUF = out[index];
            index++;
        }
    }
}
