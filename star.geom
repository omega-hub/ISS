#version 150 compatibility
#extension GL_EXT_geometry_shader4: enable
#extension GL_ARB_gpu_shader5 : enable

//uniform float pointScale;

flat out vec4 eye_position;
flat out float sphere_radius;

//uniform float globalAlpha;

void
main(void)
{
        float pointScale = 10000 * gl_FrontColorIn[0].a;
        
    	sphere_radius =  pointScale * 2.0;
    	float halfsize = sphere_radius * 0.5;

    	gl_FrontColor = gl_FrontColorIn[0];
    	//gl_FrontColor.a = globalAlpha;

    	eye_position = gl_PositionIn[0];

    	gl_TexCoord[0].st = vec2(1.0,-1.0);
    	gl_Position = gl_PositionIn[0];
    	gl_Position.xy += vec2(halfsize, -halfsize);
    	gl_Position = gl_ProjectionMatrix * gl_Position;
    	EmitVertex();
    
    	gl_TexCoord[0].st = vec2(1.0,1.0);
    	gl_Position = gl_PositionIn[0];
    	gl_Position.xy += vec2(halfsize, halfsize);
    	gl_Position = gl_ProjectionMatrix * gl_Position;
    	EmitVertex();

    	gl_TexCoord[0].st = vec2(-1.0,-1.0);
    	gl_Position = gl_PositionIn[0];
    	gl_Position.xy += vec2(-halfsize, -halfsize);
    	gl_Position = gl_ProjectionMatrix * gl_Position;
    	EmitVertex();

    	gl_TexCoord[0].st = vec2(-1.0,1.0);
    	gl_Position = gl_PositionIn[0];
    	gl_Position.xy += vec2(-halfsize, halfsize);
    	gl_Position = gl_ProjectionMatrix * gl_Position;
    	EmitVertex();
    
    	EndPrimitive();
}
