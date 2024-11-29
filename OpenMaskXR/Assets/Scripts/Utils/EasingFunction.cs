/*
 * Created by C.J. Kimberlin
 * 
 * The MIT License (MIT)
 * 
 * Copyright (c) 2019
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 * 
 * 
 * TERMS OF USE - EASING EQUATIONS
 * Open source under the BSD License.
 * Copyright (c)2001 Robert Penner
 * All rights reserved.
 * Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
 * Neither the name of the author nor the names of contributors may be used to endorse or promote products derived from this software without specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE 
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 *
 * ============= Description =============
 *
 * Below is an example of how to use the easing functions in the file. There is a getting function that will return the function
 * from an enum. This is useful since the enum can be exposed in the editor and then the function queried during Start().
 * 
 * EasingFunction.Ease ease = EasingFunction.Ease.EaseInOutQuad;
 * EasingFunction.EasingFunc func = GetEasingFunction(ease;
 * 
 * float value = func(0, 10, 0.67f);
 * 
 * EasingFunction.EaseingFunc derivativeFunc = GetEasingFunctionDerivative(ease);
 * 
 * float derivativeValue = derivativeFunc(0, 10, 0.67f);
 */

using System;
using UnityEngine;

public enum EaseType : byte
{
    EaseInQuad = 0,
    EaseOutQuad,
    EaseInOutQuad,
    EaseInCubic,
    EaseOutCubic,
    EaseInOutCubic,
    EaseInQuart,
    EaseOutQuart,
    EaseInOutQuart,
    EaseInQuint,
    EaseOutQuint,
    EaseInOutQuint,
    EaseInSine,
    EaseOutSine,
    EaseInOutSine,
    EaseInExpo,
    EaseOutExpo,
    EaseInOutExpo,
    EaseInCirc,
    EaseOutCirc,
    EaseInOutCirc,
    Linear,
    Spring,
    EaseInBounce,
    EaseOutBounce,
    EaseInOutBounce,
    EaseInBack,
    EaseOutBack,
    EaseInOutBack,
    EaseInElastic,
    EaseOutElastic,
    EaseInOutElastic,
}
public static class EasingFunction
{

    private const float NATURAL_LOG_OF_2 = 0.693147181f;

    /// Easing functions ///

    public static float Linear(float start, float end, float value) => Mathf.Lerp(start, end, value);

    public static float Spring(float start, float end, float value)
    {
        value = Mathf.Clamp01(value);
        value = (MathF.Sin(value * MathF.PI * (0.2f + 2.5f * value * value * value)) * MathF.Pow(1f - value, 2.2f) + value) * (1f + (1.2f * (1f - value)));
        return start + (end - start) * value;
    }

    public static float EaseInQuad(float start, float end, float value)
    {
        end -= start;
        return end * value * value + start;
    }

    public static float EaseOutQuad(float start, float end, float value)
    {
        end -= start;
        return -end * value * (value - 2) + start;
    }

    public static float EaseInOutQuad(float start, float end, float value)
    {
        value /= .5f;
        end -= start;
        if (value < 1) return end * 0.5f * value * value + start;
        value--;
        return -end * 0.5f * (value * (value - 2) - 1) + start;
    }

    public static float EaseInCubic(float start, float end, float value)
    {
        end -= start;
        return end * value * value * value + start;
    }

    public static float EaseOutCubic(float start, float end, float value)
    {
        value--;
        end -= start;
        return end * (value * value * value + 1) + start;
    }

    public static float EaseInOutCubic(float start, float end, float value)
    {
        value /= .5f;
        end -= start;
        if (value < 1) return end * 0.5f * value * value * value + start;
        value -= 2;
        return end * 0.5f * (value * value * value + 2) + start;
    }

    public static float EaseInQuart(float start, float end, float value)
    {
        end -= start;
        return end * value * value * value * value + start;
    }

    public static float EaseOutQuart(float start, float end, float value)
    {
        value--;
        end -= start;
        return -end * (value * value * value * value - 1) + start;
    }

    public static float EaseInOutQuart(float start, float end, float value)
    {
        value /= .5f;
        end -= start;
        if (value < 1) return end * 0.5f * value * value * value * value + start;
        value -= 2;
        return -end * 0.5f * (value * value * value * value - 2) + start;
    }

    public static float EaseInQuint(float start, float end, float value)
    {
        end -= start;
        return end * value * value * value * value * value + start;
    }

    public static float EaseOutQuint(float start, float end, float value)
    {
        value--;
        end -= start;
        return end * (value * value * value * value * value + 1) + start;
    }

    public static float EaseInOutQuint(float start, float end, float value)
    {
        value /= .5f;
        end -= start;
        if (value < 1) return end * 0.5f * value * value * value * value * value + start;
        value -= 2;
        return end * 0.5f * (value * value * value * value * value + 2) + start;
    }

    public static float EaseInSine(float start, float end, float value)
    {
        end -= start;
        return -end * MathF.Cos(value * (MathF.PI * 0.5f)) + end + start;
    }

    public static float EaseOutSine(float start, float end, float value)
    {
        end -= start;
        return end * MathF.Sin(value * (MathF.PI * 0.5f)) + start;
    }

    public static float EaseInOutSine(float start, float end, float value)
    {
        end -= start;
        return -end * 0.5f * (MathF.Cos(MathF.PI * value) - 1) + start;
    }

    public static float EaseInExpo(float start, float end, float value)
    {
        end -= start;
        return end * MathF.Pow(2, 10 * (value - 1)) + start;
    }

    public static float EaseOutExpo(float start, float end, float value)
    {
        end -= start;
        return end * (-MathF.Pow(2, -10 * value) + 1) + start;
    }

    public static float EaseInOutExpo(float start, float end, float value)
    {
        value /= .5f;
        end -= start;

        if (value < 1)
            return end * 0.5f * MathF.Pow(2, 10 * (value - 1)) + start;

        value--;

        return end * 0.5f * (-MathF.Pow(2, -10 * value) + 2) + start;
    }

    public static float EaseInCirc(float start, float end, float value)
    {
        end -= start;
        return -end * (MathF.Sqrt(1 - value * value) - 1) + start;
    }

    public static float EaseOutCirc(float start, float end, float value)
    {
        value--;
        end -= start;
        return end * MathF.Sqrt(1 - value * value) + start;
    }

    public static float EaseInOutCirc(float start, float end, float value)
    {
        value /= .5f;
        end -= start;
        if (value < 1) return -end * 0.5f * (MathF.Sqrt(1 - value * value) - 1) + start;
        value -= 2;
        return end * 0.5f * (MathF.Sqrt(1 - value * value) + 1) + start;
    }

    public static float EaseInBounce(float start, float end, float value)
    {
        end -= start;
        float d = 1f;
        return end - EaseOutBounce(0, end, d - value) + start;
    }

    public static float EaseOutBounce(float start, float end, float value)
    {
        value /= 1f;
        end -= start;
        if (value < (1 / 2.75f))
        {
            return end * (7.5625f * value * value) + start;
        }
        else if (value < (2 / 2.75f))
        {
            value -= (1.5f / 2.75f);
            return end * (7.5625f * (value) * value + .75f) + start;
        }
        else if (value < (2.5 / 2.75))
        {
            value -= (2.25f / 2.75f);
            return end * (7.5625f * (value) * value + .9375f) + start;
        }
        else
        {
            value -= (2.625f / 2.75f);
            return end * (7.5625f * (value) * value + .984375f) + start;
        }
    }

    public static float EaseInOutBounce(float start, float end, float value)
    {
        end -= start;
        float d = 1f;
        if (value < d * 0.5f) return EaseInBounce(0, end, value * 2) * 0.5f + start;
        else return EaseOutBounce(0, end, value * 2 - d) * 0.5f + end * 0.5f + start;
    }

    public static float EaseInBack(float start, float end, float value)
    {
        end -= start;
        value /= 1;
        float s = 1.70158f;
        return end * (value) * value * ((s + 1) * value - s) + start;
    }

    public static float EaseOutBack(float start, float end, float value)
    {
        float s = 1.70158f;
        end -= start;
        value = (value) - 1;
        return end * ((value) * value * ((s + 1) * value + s) + 1) + start;
    }

    public static float EaseInOutBack(float start, float end, float value)
    {
        float s = 1.70158f;
        end -= start;
        value /= .5f;
        if ((value) < 1)
        {
            s *= (1.525f);
            return end * 0.5f * (value * value * (((s) + 1) * value - s)) + start;
        }
        value -= 2;
        s *= (1.525f);
        return end * 0.5f * ((value) * value * (((s) + 1) * value + s) + 2) + start;
    }

    public static float EaseInElastic(float start, float end, float value)
    {
        end -= start;

        float d = 1f;
        float p = d * .3f;
        float s;
        float a = 0;

        if (value == 0)
            return start;

        if ((value /= d) == 1)
            return start + end;

        if (a == 0f || a < MathF.Abs(end))
        {
            a = end;
            s = p / 4;
        }
        else
            s = p / (2 * MathF.PI) * MathF.Asin(end / a);

        return -(a * MathF.Pow(2, 10 * (value -= 1)) * MathF.Sin((value * d - s) * (2 * MathF.PI) / p)) + start;
    }

    public static float EaseOutElastic(float start, float end, float value)
    {
        end -= start;

        float d = 1f;
        float p = d * .3f;
        float s;
        float a = 0;

        if (value == 0) return start;

        if ((value /= d) == 1) return start + end;

        if (a == 0f || a < MathF.Abs(end))
        {
            a = end;
            s = p * 0.25f;
        }
        else
        {
            s = p / (2 * MathF.PI) * MathF.Asin(end / a);
        }

        return (a * MathF.Pow(2, -10 * value) * MathF.Sin((value * d - s) * (2 * MathF.PI) / p) + end + start);
    }

    public static float EaseInOutElastic(float start, float end, float value)
    {
        end -= start;

        float d = 1f;
        float p = d * .3f;
        float s;
        float a = 0;

        if (value == 0) return start;

        if ((value /= d * 0.5f) == 2) return start + end;

        if (a == 0f || a < MathF.Abs(end))
        {
            a = end;
            s = p / 4;
        }
        else
        {
            s = p / (2 * MathF.PI) * MathF.Asin(end / a);
        }

        if (value < 1) return -0.5f * (a * MathF.Pow(2, 10 * (value -= 1)) * MathF.Sin((value * d - s) * (2 * MathF.PI) / p)) + start;
        return a * MathF.Pow(2, -10 * (value -= 1)) * MathF.Sin((value * d - s) * (2 * MathF.PI) / p) * 0.5f + end + start;
    }

    //
    // These are derived functions that the motor can use to get the speed at a specific time.
    //
    // The easing functions all work with a normalized time (0 to 1) and the returned value here
    // reflects that. Values returned here should be divided by the actual time.
    //
    // TODO: These functions have not had the testing they deserve. If there is odd behavior around
    //       dash speeds then this would be the first place I'd look.

    public static float LinearD(float start, float end, float value) => end - start;

    public static float EaseInQuadD(float start, float end, float value) => 2f * (end - start) * value;

    public static float EaseOutQuadD(float start, float end, float value)
    {
        end -= start;
        return -end * value - end * (value - 2);
    }

    public static float EaseInOutQuadD(float start, float end, float value)
    {
        value /= .5f;
        end -= start;

        if (value < 1)
        {
            return end * value;
        }

        value--;

        return end * (1 - value);
    }

    public static float EaseInCubicD(float start, float end, float value) => 3f * (end - start) * value * value;

    public static float EaseOutCubicD(float start, float end, float value)
    {
        value--;
        end -= start;
        return 3f * end * value * value;
    }

    public static float EaseInOutCubicD(float start, float end, float value)
    {
        value /= .5f;
        end -= start;

        if (value < 1)
        {
            return (3f / 2f) * end * value * value;
        }

        value -= 2;

        return (3f / 2f) * end * value * value;
    }

    public static float EaseInQuartD(float start, float end, float value)
    {
        return 4f * (end - start) * value * value * value;
    }

    public static float EaseOutQuartD(float start, float end, float value)
    {
        value--;
        end -= start;
        return -4f * end * value * value * value;
    }

    public static float EaseInOutQuartD(float start, float end, float value)
    {
        value /= .5f;
        end -= start;

        if (value < 1)
        {
            return 2f * end * value * value * value;
        }

        value -= 2;

        return -2f * end * value * value * value;
    }

    public static float EaseInQuintD(float start, float end, float value)
    {
        return 5f * (end - start) * value * value * value * value;
    }

    public static float EaseOutQuintD(float start, float end, float value)
    {
        value--;
        end -= start;
        return 5f * end * value * value * value * value;
    }

    public static float EaseInOutQuintD(float start, float end, float value)
    {
        value /= .5f;
        end -= start;

        if (value < 1)
        {
            return (5f / 2f) * end * value * value * value * value;
        }

        value -= 2;

        return (5f / 2f) * end * value * value * value * value;
    }

    public static float EaseInSineD(float start, float end, float value)
    {
        return (end - start) * 0.5f * MathF.PI * MathF.Sin(0.5f * MathF.PI * value);
    }

    public static float EaseOutSineD(float start, float end, float value)
    {
        end -= start;
        return (MathF.PI * 0.5f) * end * MathF.Cos(value * (MathF.PI * 0.5f));
    }

    public static float EaseInOutSineD(float start, float end, float value)
    {
        end -= start;
        return end * 0.5f * MathF.PI * MathF.Sin(MathF.PI * value);
    }

    public static float EaseInExpoD(float start, float end, float value) => 10f * NATURAL_LOG_OF_2 * (end - start) * MathF.Pow(2f, 10f * (value - 1));

    public static float EaseOutExpoD(float start, float end, float value)
    {
        end -= start;
        return 5f * NATURAL_LOG_OF_2 * end * MathF.Pow(2f, 1f - 10f * value);
    }

    public static float EaseInOutExpoD(float start, float end, float value)
    {
        value /= .5f;
        end -= start;

        if (value < 1)
            return 5f * NATURAL_LOG_OF_2 * end * MathF.Pow(2f, 10f * (value - 1));

        value--;

        return (5f * NATURAL_LOG_OF_2 * end) / (MathF.Pow(2f, 10f * value));
    }

    public static float EaseInCircD(float start, float end, float value) => (end - start) * value / MathF.Sqrt(1f - value * value);

    public static float EaseOutCircD(float start, float end, float value)
    {
        value--;
        end -= start;
        return (-end * value) / MathF.Sqrt(1f - value * value);
    }

    public static float EaseInOutCircD(float start, float end, float value)
    {
        value /= .5f;
        end -= start;

        if (value < 1)
        {
            return (end * value) / (2f * MathF.Sqrt(1f - value * value));
        }

        value -= 2;

        return (-end * value) / (2f * MathF.Sqrt(1f - value * value));
    }

    public static float EaseInBounceD(float start, float end, float value)
    {
        end -= start;
        float d = 1f;

        return EaseOutBounceD(0, end, d - value);
    }

    public static float EaseOutBounceD(float start, float end, float value)
    {
        value /= 1f;
        end -= start;

        if (value < (1 / 2.75f))
        {
            return 2f * end * 7.5625f * value;
        }
        else if (value < (2 / 2.75f))
        {
            value -= (1.5f / 2.75f);
            return 2f * end * 7.5625f * value;
        }
        else if (value < (2.5 / 2.75))
        {
            value -= (2.25f / 2.75f);
            return 2f * end * 7.5625f * value;
        }
        else
        {
            value -= (2.625f / 2.75f);
            return 2f * end * 7.5625f * value;
        }
    }

    public static float EaseInOutBounceD(float start, float end, float value)
    {
        end -= start;
        float d = 1f;

        return value < d * 0.5f ? EaseInBounceD(0, end, value * 2) * 0.5f : EaseOutBounceD(0, end, value * 2 - d) * 0.5f;
    }

    public static float EaseInBackD(float start, float end, float value)
    {
        const float s = 1.70158f;
        return 3f * (s + 1f) * (end - start) * value * value - 2f * s * (end - start) * value;
    }

    public static float EaseOutBackD(float start, float end, float value)
    {
        const float s = 1.70158f;
        end -= start;
        value = (value) - 1;

        return end * ((s + 1f) * value * value + 2f * value * ((s + 1f) * value + s));
    }

    public static float EaseInOutBackD(float start, float end, float value)
    {
        float s = 1.70158f;
        end -= start;
        value /= .5f;

        if ((value) < 1)
        {
            s *= (1.525f);
            return 0.5f * end * (s + 1) * value * value + end * value * ((s + 1f) * value - s);
        }

        value -= 2;
        s *= (1.525f);
        return 0.5f * end * ((s + 1) * value * value + 2f * value * ((s + 1f) * value + s));
    }

    public static float EaseInElasticD(float start, float end, float value)
    {
        return EaseOutElasticD(start, end, 1f - value);
    }

    public static float EaseOutElasticD(float start, float end, float value)
    {
        end -= start;

        float d = 1f;
        float p = d * .3f;
        float s;
        float a = 0;

        if (a == 0f || a < MathF.Abs(end))
        {
            a = end;
            s = p * 0.25f;
        }
        else
        {
            s = p / (2 * MathF.PI) * MathF.Asin(end / a);
        }

        return (a * MathF.PI * d * MathF.Pow(2f, 1f - 10f * value) *
            MathF.Cos((2f * MathF.PI * (d * value - s)) / p)) / p - 5f * NATURAL_LOG_OF_2 * a *
            MathF.Pow(2f, 1f - 10f * value) * MathF.Sin((2f * MathF.PI * (d * value - s)) / p);
    }

    public static float EaseInOutElasticD(float start, float end, float value)
    {
        end -= start;

        float d = 1f;
        float p = d * .3f;
        float s;
        float a = 0;

        if (a == 0f || a < MathF.Abs(end))
        {
            a = end;
            s = p / 4;
        }
        else
        {
            s = p / (2 * MathF.PI) * MathF.Asin(end / a);
        }

        if (value < 1)
        {
            value -= 1;

            return -5f * NATURAL_LOG_OF_2 * a * MathF.Pow(2f, 10f * value) * MathF.Sin(2 * MathF.PI * (d * value - 2f) / p) -
                a * MathF.PI * d * MathF.Pow(2f, 10f * value) * MathF.Cos(2 * MathF.PI * (d * value - s) / p) / p;
        }

        value -= 1;

        return a * MathF.PI * d * MathF.Cos(2f * MathF.PI * (d * value - s) / p) / (p * MathF.Pow(2f, 10f * value)) -
            5f * NATURAL_LOG_OF_2 * a * MathF.Sin(2f * MathF.PI * (d * value - s) / p) / (MathF.Pow(2f, 10f * value));
    }

    public static float SpringD(float start, float end, float value)
    {
        value = Mathf.Clamp01(value);
        end -= start;

        // Damn... Thanks http://www.derivative-calculator.net/
        // TODO: And it's a little bit wrong
        return end * (6f * (1f - value) / 5f + 1f) * (-2.2f * MathF.Pow(1f - value, 1.2f) *
            MathF.Sin(MathF.PI * value * (2.5f * value * value * value + 0.2f)) + MathF.Pow(1f - value, 2.2f) *
            (MathF.PI * (2.5f * value * value * value + 0.2f) + 7.5f * MathF.PI * value * value * value) *
            MathF.Cos(MathF.PI * value * (2.5f * value * value * value + 0.2f)) + 1f) -
            6f * end * (MathF.Pow(1 - value, 2.2f) * MathF.Sin(MathF.PI * value * (2.5f * value * value * value + 0.2f)) + value
            / 5f);

    }

    public static float EaseClamped(float start, float end, float value, EaseType type)
    {
        value = Mathf.Clamp(start, end, value);
        return Ease(start, end, value, type);
    }

    public static float Ease(float start, float end, float value, EaseType type)
    {
        switch (type)
        {
            case EaseType.EaseInQuad: return EaseInQuad(start, end, value);
            case EaseType.EaseOutQuad: return EaseOutQuad(start, end, value);
            case EaseType.EaseInOutQuad: return EaseInOutQuad(start, end, value);
            case EaseType.EaseInCubic: return EaseInCubic(start, end, value);
            case EaseType.EaseOutCubic: return EaseOutCubic(start, end, value);
            case EaseType.EaseInOutCubic: return EaseInOutCubic(start, end, value);
            case EaseType.EaseInQuart: return EaseInQuart(start, end, value);
            case EaseType.EaseOutQuart: return EaseOutQuart(start, end, value);
            case EaseType.EaseInOutQuart: return EaseInOutQuart(start, end, value);
            case EaseType.EaseInQuint: return EaseInQuint(start, end, value);
            case EaseType.EaseOutQuint: return EaseOutQuint(start, end, value);
            case EaseType.EaseInOutQuint: return EaseInOutQuint(start, end, value);
            case EaseType.EaseInSine: return EaseInSine(start, end, value);
            case EaseType.EaseOutSine: return EaseOutSine(start, end, value);
            case EaseType.EaseInOutSine: return EaseInOutSine(start, end, value);
            case EaseType.EaseInExpo: return EaseInExpo(start, end, value);
            case EaseType.EaseOutExpo: return EaseOutExpo(start, end, value);
            case EaseType.EaseInOutExpo: return EaseInOutExpo(start, end, value);
            case EaseType.EaseInCirc: return EaseInCirc(start, end, value);
            case EaseType.EaseOutCirc: return EaseOutCirc(start, end, value);
            case EaseType.EaseInOutCirc: return EaseInOutCirc(start, end, value);
            case EaseType.Linear: return Linear(start, end, value);
            case EaseType.Spring: return Spring(start, end, value);
            case EaseType.EaseInBounce: return EaseInBounce(start, end, value);
            case EaseType.EaseOutBounce: return EaseOutBounce(start, end, value);
            case EaseType.EaseInOutBounce: return EaseInOutBounce(start, end, value);
            case EaseType.EaseInBack: return EaseInBack(start, end, value);
            case EaseType.EaseOutBack: return EaseOutBack(start, end, value);
            case EaseType.EaseInOutBack: return EaseInOutBack(start, end, value);
            case EaseType.EaseInElastic: return EaseInElastic(start, end, value);
            case EaseType.EaseOutElastic: return EaseOutElastic(start, end, value);
            case EaseType.EaseInOutElastic: return EaseInOutElastic(start, end, value);
            default:
                Debug.Assert(false);
                return 0;
        }
    }

    public static Vector3 Ease(Vector3 start, Vector3 end, float value, EaseType type)
    {
        return new Vector3(Ease(start.x, end.x, value, type),
                           Ease(start.y, end.y, value, type),
                           Ease(start.z, end.z, value, type));
    }

    public delegate float Function(float start, float end, float value);

    /// <summary>
    /// Returns the function associated to the easingFunction enum. This value returned should be cached as it allocates memory
    /// to return.
    /// </summary>
    /// <param name="type">The enum associated with the easing function.</param>
    /// <returns>The easing function</returns>
    public static Function GetEasingFunction(EaseType type) => type switch
    {
        EaseType.EaseInQuad => EaseInQuad,
        EaseType.EaseOutQuad => EaseOutQuad,
        EaseType.EaseInOutQuad => EaseInOutQuad,
        EaseType.EaseInCubic => EaseInCubic,
        EaseType.EaseOutCubic => EaseOutCubic,
        EaseType.EaseInOutCubic => EaseInOutCubic,
        EaseType.EaseInQuart => EaseInQuart,
        EaseType.EaseOutQuart => EaseOutQuart,
        EaseType.EaseInOutQuart => EaseInOutQuart,
        EaseType.EaseInQuint => EaseInQuint,
        EaseType.EaseOutQuint => EaseOutQuint,
        EaseType.EaseInOutQuint => EaseInOutQuint,
        EaseType.EaseInSine => EaseInSine,
        EaseType.EaseOutSine => EaseOutSine,
        EaseType.EaseInOutSine => EaseInOutSine,
        EaseType.EaseInExpo => EaseInExpo,
        EaseType.EaseOutExpo => EaseOutExpo,
        EaseType.EaseInOutExpo => EaseInOutExpo,
        EaseType.EaseInCirc => EaseInCirc,
        EaseType.EaseOutCirc => EaseOutCirc,
        EaseType.EaseInOutCirc => EaseInOutCirc,
        EaseType.Linear => Linear,
        EaseType.Spring => Spring,
        EaseType.EaseInBounce => EaseInBounce,
        EaseType.EaseOutBounce => EaseOutBounce,
        EaseType.EaseInOutBounce => EaseInOutBounce,
        EaseType.EaseInBack => EaseInBack,
        EaseType.EaseOutBack => EaseOutBack,
        EaseType.EaseInOutBack => EaseInOutBack,
        EaseType.EaseInElastic => EaseInElastic,
        EaseType.EaseOutElastic => EaseOutElastic,
        EaseType.EaseInOutElastic => EaseInOutElastic,
        _ => null,
    };

    /// <summary>
    /// Gets the derivative function of the appropriate easing function. If you use an easing function for position then this
    /// function can get you the speed at a given time (normalized).
    /// </summary>
    /// <param name="type"></param>
    /// <returns>The derivative function</returns>
    public static Function GetEasingFunctionDerivative(EaseType type) => type switch
    {
        EaseType.EaseInQuad => EaseInQuadD,
        EaseType.EaseOutQuad => EaseOutQuadD,
        EaseType.EaseInOutQuad => EaseInOutQuadD,
        EaseType.EaseInCubic => EaseInCubicD,
        EaseType.EaseOutCubic => EaseOutCubicD,
        EaseType.EaseInOutCubic => EaseInOutCubicD,
        EaseType.EaseInQuart => EaseInQuartD,
        EaseType.EaseOutQuart => EaseOutQuartD,
        EaseType.EaseInOutQuart => EaseInOutQuartD,
        EaseType.EaseInQuint => EaseInQuintD,
        EaseType.EaseOutQuint => EaseOutQuintD,
        EaseType.EaseInOutQuint => EaseInOutQuintD,
        EaseType.EaseInSine => EaseInSineD,
        EaseType.EaseOutSine => EaseOutSineD,
        EaseType.EaseInOutSine => EaseInOutSineD,
        EaseType.EaseInExpo => EaseInExpoD,
        EaseType.EaseOutExpo => EaseOutExpoD,
        EaseType.EaseInOutExpo => EaseInOutExpoD,
        EaseType.EaseInCirc => EaseInCircD,
        EaseType.EaseOutCirc => EaseOutCircD,
        EaseType.EaseInOutCirc => EaseInOutCircD,
        EaseType.Linear => LinearD,
        EaseType.Spring => SpringD,
        EaseType.EaseInBounce => EaseInBounceD,
        EaseType.EaseOutBounce => EaseOutBounceD,
        EaseType.EaseInOutBounce => EaseInOutBounceD,
        EaseType.EaseInBack => EaseInBackD,
        EaseType.EaseOutBack => EaseOutBackD,
        EaseType.EaseInOutBack => EaseInOutBackD,
        EaseType.EaseInElastic => EaseInElasticD,
        EaseType.EaseOutElastic => EaseOutElasticD,
        EaseType.EaseInOutElastic => EaseInOutElasticD,
        _ => null,
    };
}
