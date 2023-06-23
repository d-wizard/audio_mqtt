/* Copyright 2023 Dan Williams. All Rights Reserved.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this
 * software and associated documentation files (the "Software"), to deal in the Software
 * without restriction, including without limitation the rights to use, copy, modify, merge,
 * publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons
 * to whom the Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all copies or
 * substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 * INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
 * PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
 * FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
 * OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 */
#include <stdio.h>
#include <stdint.h>
#include <memory>
#include <chrono>
#include <thread>
#include <mutex>
#include <condition_variable>
#include "alsaMic.h"

// #define ENABLE_PLOTTING
#ifdef ENABLE_PLOTTING
#include "smartPlotMessage.h"
#endif

///////////////////////////////////////////////////////////////////////////////

static constexpr double TIME_BETWEEN = 15.0; // 15 seconds

///////////////////////////////////////////////////////////////////////////////

static std::thread g_watchdog_thread;
static std::mutex g_watchdog_mutex;
static std::condition_variable g_watchdog_condVar;
static double g_watchdog_killTime = 150.0;

///////////////////////////////////////////////////////////////////////////////

// Microphone Capture
static std::unique_ptr<AlsaMic> g_mic;

static bool firstTime = true;
static int64_t lastUpdateTime = 0;
static int64_t average_sum = 0;
static int average_count = 0;

///////////////////////////////////////////////////////////////////////////////

// MQTT values from command line
static std::string mqtt_pythonScriptPath = "";
static std::string mqtt_broker_ipAddr = "127.0.0.1";
static uint16_t mqtt_broker_port = 1883;
static std::string mqtt_topic = "default_topic_name";

///////////////////////////////////////////////////////////////////////////////

static double getNowTime()
{
   auto timePoint = std::chrono::steady_clock::now().time_since_epoch();
   return std::chrono::duration<double>(timePoint).count();
}

///////////////////////////////////////////////////////////////////////////////

static void publishMqtt(int32_t value)
{
   std::string cmd = "python3 " + mqtt_pythonScriptPath + " -b " + mqtt_broker_ipAddr + " -p " + std::to_string(mqtt_broker_port) + " -t " + mqtt_topic + " -m " + std::to_string(value) + " &";
   // printf("%s\n", cmd.c_str());
   system(cmd.c_str());
}

///////////////////////////////////////////////////////////////////////////////

static void alsaMicSamples(void* usrPtr, int16_t* samples, size_t numSamp)
{
   int32_t maxValue = 0;
   for(size_t i = 0; i < numSamp; ++i)
   {
      int32_t value = samples[i];
      value = value >= 0 ? value : -value; // Do abs
      if(value > maxValue)
         maxValue = value;
   }

   average_sum += maxValue;
   average_count++;

   auto nowTime = getNowTime();

   if(firstTime)
   {
      firstTime = false;
      lastUpdateTime = nowTime;
   }

   if((nowTime - lastUpdateTime) > TIME_BETWEEN)
   {
      int32_t average = int32_t(average_sum / average_count);
      lastUpdateTime = nowTime;
      average_sum = 0;
      average_count = 0;

      publishMqtt(average); // Publish MQTT data.

      // wake the watchdog.
      {
         std::lock_guard<std::mutex> lock(g_watchdog_mutex);
         g_watchdog_condVar.notify_all();
      }

#ifdef ENABLE_PLOTTING
      smartPlot_1D(&average, E_INT_32, 1, 10000, -1, "Avg", "value");
#endif
   }

#ifdef ENABLE_PLOTTING
   smartPlot_1D(&maxValue, E_INT_32, 1, 10000, -1, "Max", "PcmValue");
   // smartPlot_1D(samples, E_INT_16, numSamp, 44100*10, -1, "Mic", "samples");
#endif

}

///////////////////////////////////////////////////////////////////////////////

void watchdogThread()
{
   std::unique_lock<std::mutex> lock(g_watchdog_mutex);
   auto timeoutNs = std::chrono::nanoseconds(uint64_t(g_watchdog_killTime*1e9));
   while(true)
   {
      if(g_watchdog_condVar.wait_for(lock, timeoutNs) == std::cv_status::timeout)
      {
         printf("watchdog exit\n");
         exit(1);
      }
   }
}

///////////////////////////////////////////////////////////////////////////////

int main (int argc, char *argv[])
{
#ifdef ENABLE_PLOTTING
   smartPlot_createFlushThread(250);
#endif

   if(argc > 1)
   {
      mqtt_pythonScriptPath = std::string(argv[1]);
   }
   else
   {
      printf("Invalid command line args - Need to specify path to MQTT publisher python script.\n");
      return -1;
   }

   if(argc > 2)
      mqtt_broker_ipAddr = std::string(argv[2]);
   if(argc > 3)
      mqtt_broker_port = atoi(argv[3]);
   if(argc > 4)
      mqtt_topic = std::string(argv[4]);

   // Start watchdog
   g_watchdog_thread = std::thread(watchdogThread);

   g_mic.reset(new AlsaMic("hw:1", 44100, 1024, 1, alsaMicSamples, nullptr));

   sleep(0x7FFFFFFF);

   return 0;
}
