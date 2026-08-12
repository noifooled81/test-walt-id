using System.Reflection;
using Application.Services;

namespace Application;

public class Program
{
    public static void Main(string[] args)
    {
        Console.WriteLine("=== walt.id Entity Config Generator & Appender ===");

        var domainAssembly = Assembly.GetAssembly(typeof(Domain.Credentials.MyUniCredential))
                             ?? AppDomain.CurrentDomain.GetAssemblies().FirstOrDefault(a => a.GetName().Name == "Domain");

        if (domainAssembly == null)
        {
            Console.WriteLine("Error: Could not locate Domain assembly.");
            return;
        }

        var credentialTypes = domainAssembly.GetTypes()
            .Where(t => t.IsClass && !t.IsAbstract &&
                       (t.Namespace?.StartsWith("Domain.Credentials") == true || t.Name.EndsWith("Credential")))
            .ToList();

        if (credentialTypes.Count == 0)
        {
            Console.WriteLine("No credential types found in Domain.");
            return;
        }

        // Define paths to target walt.id config directory
        string baseDir = Directory.GetCurrentDirectory();
        string targetConfigDir = Path.Combine(baseDir, "waltid", "issuer-api2", "config");

        string metadataTarget = Path.Combine(targetConfigDir, "credential-issuer-metadata.conf");
        string metadataBak = Path.Combine(targetConfigDir, "credential-issuer-metadata.conf.bak");

        string profilesTarget = Path.Combine(targetConfigDir, "issuer2-profiles.conf");
        string profilesBak = Path.Combine(targetConfigDir, "issuer2-profiles.conf.bak");

        bool targetExists = Directory.Exists(targetConfigDir);

        if (targetExists)
        {
            // 1st Step: Create backup of default config files if .bak does not exist yet
            if (File.Exists(metadataTarget) && !File.Exists(metadataBak))
            {
                File.Copy(metadataTarget, metadataBak);
                Console.WriteLine($"[+] Created backup: {metadataBak}");
            }

            if (File.Exists(profilesTarget) && !File.Exists(profilesBak))
            {
                File.Copy(profilesTarget, profilesBak);
                Console.WriteLine($"[+] Created backup: {profilesBak}");
            }

            // Reset target files from .bak before appending new generated configs
            if (File.Exists(metadataBak))
            {
                File.Copy(metadataBak, metadataTarget, overwrite: true);
                Console.WriteLine($"[+] Reset {metadataTarget} from backup");
            }

            if (File.Exists(profilesBak))
            {
                File.Copy(profilesBak, profilesTarget, overwrite: true);
                Console.WriteLine($"[+] Reset {profilesTarget} from backup");
            }
        }

        foreach (var credentialType in credentialTypes)
        {
            Console.WriteLine($"\nProcessing Entity: {credentialType.FullName}");

            var result = WaltIdConfigGenerator.GenerateForType(credentialType);

            if (targetExists && File.Exists(metadataTarget) && File.Exists(profilesTarget))
            {
                File.AppendAllText(metadataTarget, "\n" + result.MetadataConfContent);
                File.AppendAllText(profilesTarget, "\n" + result.ProfilesConfContent);
                Console.WriteLine($"[+] Appended {credentialType.Name} config to waltid/issuer-api2/config files");
            }

            // Also output standalone files in waltid-config directory
            string outputDir = Path.Combine(baseDir, "waltid-config");
            Directory.CreateDirectory(outputDir);
            File.WriteAllText(Path.Combine(outputDir, "credential-issuer-metadata.conf"), result.MetadataConfContent);
            File.WriteAllText(Path.Combine(outputDir, "issuer2-profiles.conf"), result.ProfilesConfContent);

            Console.WriteLine("\n------------------------------------------------------------");
            Console.WriteLine($"GENERATED CONFIG FOR: {credentialType.Name}");
            Console.WriteLine("------------------------------------------------------------");
            Console.WriteLine(result.MetadataConfContent);
            Console.WriteLine(result.ProfilesConfContent);
        }
    }
}
