#version 130
in vec2 texcoord;
out vec4 fragColor;
uniform sampler2D p3d_Texture0;

void main() {
    vec4 color = texture(p3d_Texture0, texcoord);
    vec4 bloom = color * 2.0; // Simple bloom effect by doubling the brightness
    fragColor = bloom;
}
