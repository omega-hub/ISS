@surfaceShader

uniform float unif_Shininess;
uniform float unif_Gloss;

varying vec3 var_Normal;

///////////////////////////////////////////////////////////////////////////////////////////////////
SurfaceData getSurfaceData(void)
{
	SurfaceData sd;
	float x;
	x = 1.0 - dot(normalize(var_Normal), -normalize(var_EyeVector).xyz);
	
	float f;
	f =/* a * exp(-e)*/ pow(x, 16.0);
	
    	sd.albedo = gl_FrontMaterial.diffuse; 
	sd.emissive = gl_FrontMaterial.emission;
	sd.emissive.a = f;
	sd.shininess = unif_Shininess;
	sd.gloss = unif_Gloss;
	sd.normal = normalize(var_Normal);
	
	return sd;
}
