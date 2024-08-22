#version 450 core

in vec2 fragmentTexCoord;

uniform float u_amplitude[64]; // amplitude input from python code (one value per frequency bin)

out vec4 color;

// signed distance function (SDF) for drawing rectangles (bars) with specific dimensions onto the screen at specific location
// see https://iquilezles.org/articles/distfunctions2d/ if you want to learn more
float sdBox(in vec2 p, in vec2 loc, in vec2 dim)
{
    vec2 d = abs(p-loc) - dim;
    return length(max(d,0.0)) + min(max(d.x,d.y),0.0);
}

void main()
{
    vec2 uv = fragmentTexCoord;
    vec3 col = vec3(1.0, 0.0, 1.0); // set the color of the bars and the glow effect
    float fin = 0; // final brightness

    // for each pixel/fragment on the screen, its distance to all 64 bars is calculated
    // each distance is converted into a brightness level (think the amount of light the pixel receives from each bar)
    // the 64 brightness values are all added together to determine the final  brightness
    // which is then multiplied by the base color
    for (int i = 0; i < 64; ++i)
    {
        vec2 loc = vec2((i + 0.5) / 64.0, 0.5); // determines the location of the center of each bar
        vec2 dim = vec2(0.12/64.0, ((u_amplitude[i] - 40) / 400.0)); // determines dimensions of each bar (high amplitude = tall bar)
        float d = clamp(sdBox(uv, vec2(loc.x, loc.y), dim), 0.0, 1.0); // see what happens when you set the minimum of the clamp to 0.01 or 0.001 rather than 0.0
        fin += 0.0008 / d; // using the inverse (dividing by d) creates a cool glow effect (number on the left controls glow intensity)
    }
    
    col *= fin; // we apply our functions to the color
    color = vec4(col.rgb, 1.0);
}