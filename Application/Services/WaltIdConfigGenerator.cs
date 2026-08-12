using System.Collections;
using System.Reflection;
using System.Text;

namespace Application.Services;

public static class WaltIdConfigGenerator
{
    public record GeneratedConfigFiles(
        string CredentialType,
        string MetadataConfContent,
        string ProfilesConfContent
    );

    public static GeneratedConfigFiles GenerateForType(Type credentialType, string? customScope = null, string format = "jwt_vc_json")
    {
        string typeName = credentialType.Name;
        string configId = $"{typeName}_{format}";
        string profileName = Char.ToLowerInvariant(typeName[0]) + typeName[1..];
        string scope = customScope ?? configId;

        string metadataConf = GenerateMetadataConf(typeName, configId, scope, format);

        var sampleSubject = GenerateSampleDataForType(credentialType);
        string profilesConf = GenerateProfilesConf(typeName, profileName, configId, sampleSubject);

        return new GeneratedConfigFiles(typeName, metadataConf, profilesConf);
    }

    private static string GenerateMetadataConf(string typeName, string configId, string scope, string format)
    {
        var sb = new StringBuilder();
        sb.AppendLine("credentialConfigurations = {");
        sb.AppendLine($"  \"{configId}\" = {{");
        sb.AppendLine($"    format = \"{format}\"");
        sb.AppendLine($"    scope = \"{scope}\"");
        sb.AppendLine("    cryptographic_binding_methods_supported = [\"jwk\", \"did:key\", \"did:web\"]");
        sb.AppendLine("    credential_signing_alg_values_supported = [\"ES256\"]");
        sb.AppendLine("    proof_types_supported = {");
        sb.AppendLine("      jwt = {");
        sb.AppendLine("        proof_signing_alg_values_supported = [\"ES256\", \"EdDSA\"]");
        sb.AppendLine("      }");
        sb.AppendLine("    }");
        sb.AppendLine("    credential_definition = {");
        sb.AppendLine($"      type = [\"VerifiableCredential\", \"{typeName}\"]");
        sb.AppendLine("    }");
        sb.AppendLine("  }");
        sb.AppendLine("}");
        return sb.ToString();
    }

    private static string GenerateProfilesConf(string typeName, string profileName, string configId, Dictionary<string, object?> sampleSubjectData)
    {
        var sb = new StringBuilder();
        sb.AppendLine("profiles = {");
        sb.AppendLine($"  {profileName} = {{");
        sb.AppendLine($"    name = \"{SplitCamelCase(typeName)}\"");
        sb.AppendLine($"    credentialConfigurationId = \"{configId}\"");
        sb.AppendLine("    issuerKey = ${defaultIssuerKey}");
        sb.AppendLine("    issuerDid = ${defaultIssuerDid}");
        sb.AppendLine("    credentialData = {");
        sb.AppendLine("      \"@context\" = [");
        sb.AppendLine("        \"https://www.w3.org/2018/credentials/v1\"");
        sb.AppendLine("      ]");
        sb.AppendLine($"      type = [\"VerifiableCredential\", \"{typeName}\"]");
        sb.AppendLine("      credentialSubject = {");

        FormatHoconDictionary(sb, sampleSubjectData, indentLevel: 8);

        sb.AppendLine("      }");
        sb.AppendLine("    }");
        sb.AppendLine("    mapping = {");
        sb.AppendLine("      id = \"<uuid>\"");
        sb.AppendLine("      issuer = { id = \"<issuerDid>\" }");
        sb.AppendLine("      credentialSubject = { id = \"<subjectDid>\" }");
        sb.AppendLine("      issuanceDate = \"<timestamp>\"");
        sb.AppendLine("      expirationDate = \"<timestamp-in:365d>\"");
        sb.AppendLine("    }");
        sb.AppendLine("  }");
        sb.AppendLine("}");
        return sb.ToString();
    }

    private static Dictionary<string, object?> GenerateSampleDataForType(Type type)
    {
        var result = new Dictionary<string, object?>();

        var properties = type.GetProperties(BindingFlags.Public | BindingFlags.Instance);
        foreach (var prop in properties)
        {
            // Skip properties marked with [JsonIgnore]
            if (prop.GetCustomAttribute<System.Text.Json.Serialization.JsonIgnoreAttribute>() != null)
            {
                continue;
            }

            string key = prop.Name switch
            {
                "GPA" => "gpa",
                _ => Char.ToLowerInvariant(prop.Name[0]) + prop.Name[1..]
            };
            result[key] = GetDefaultValueForType(prop.PropertyType, prop.Name);
        }

        return result;
    }

    private static object? GetDefaultValueForType(Type propType, string propName)
    {
        Type underlyingType = Nullable.GetUnderlyingType(propType) ?? propType;

        if (underlyingType == typeof(string))
        {
            if (propName.Equals("UniName", StringComparison.OrdinalIgnoreCase)) return "My Uni";
            if (propName.Equals("FirstName", StringComparison.OrdinalIgnoreCase)) return "James";
            if (propName.Equals("LastName", StringComparison.OrdinalIgnoreCase)) return "Smith";
            if (propName.Equals("Name", StringComparison.OrdinalIgnoreCase)) return "School of Computer Science";
            if (propName.Equals("School", StringComparison.OrdinalIgnoreCase)) return "School of Computer Science";
            if (propName.Equals("Program", StringComparison.OrdinalIgnoreCase)) return "Software Engineering";
            return propName;
        }

        if (underlyingType == typeof(int) || underlyingType == typeof(long))
        {
            if (propName.Equals("Intake", StringComparison.OrdinalIgnoreCase)) return 2021;
            return 100;
        }

        if (underlyingType == typeof(double) || underlyingType == typeof(float) || underlyingType == typeof(decimal))
        {
            if (propName.Equals("GPA", StringComparison.OrdinalIgnoreCase)) return 4.0;
            return 3.5;
        }

        if (underlyingType == typeof(bool))
        {
            return true;
        }

        if (underlyingType == typeof(DateTime) || underlyingType == typeof(DateTimeOffset))
        {
            return "2000-01-01T00:00:00Z";
        }

        if (underlyingType.IsEnum)
        {
            var values = Enum.GetNames(underlyingType);
            return values.Length > 0 ? values[0] : "Default";
        }

        if (typeof(IEnumerable).IsAssignableFrom(underlyingType) && underlyingType != typeof(string))
        {
            return new List<string> { "Software Engineering" };
        }

        if (underlyingType.IsClass)
        {
            return GenerateSampleDataForType(underlyingType);
        }

        return null;
    }

    private static void FormatHoconDictionary(StringBuilder sb, Dictionary<string, object?> dict, int indentLevel)
    {
        string indent = new string(' ', indentLevel);
        foreach (var (key, value) in dict)
        {
            if (value is Dictionary<string, object?> nestedDict)
            {
                sb.AppendLine($"{indent}{key} = {{");
                FormatHoconDictionary(sb, nestedDict, indentLevel + 2);
                sb.AppendLine($"{indent}}}");
            }
            else if (value is IEnumerable list && !(value is string))
            {
                var items = list.Cast<object>().Select(x => $"\"{x}\"");
                sb.AppendLine($"{indent}{key} = [{string.Join(", ", items)}]");
            }
            else if (value is string str)
            {
                sb.AppendLine($"{indent}{key} = \"{str}\"");
            }
            else if (value is double d)
            {
                sb.AppendLine($"{indent}{key} = {d.ToString("0.0", System.Globalization.CultureInfo.InvariantCulture)}");
            }
            else if (value is float f)
            {
                sb.AppendLine($"{indent}{key} = {f.ToString("0.0", System.Globalization.CultureInfo.InvariantCulture)}");
            }
            else if (value is decimal dec)
            {
                sb.AppendLine($"{indent}{key} = {dec.ToString("0.0", System.Globalization.CultureInfo.InvariantCulture)}");
            }
            else if (value is int || value is long || value is bool)
            {
                sb.AppendLine($"{indent}{key} = {value.ToString()?.ToLowerInvariant()}");
            }
            else
            {
                sb.AppendLine($"{indent}{key} = \"{value}\"");
            }
        }
    }

    private static string SplitCamelCase(string str)
    {
        return System.Text.RegularExpressions.Regex.Replace(str, "(\\B[A-Z])", " $1");
    }
}
