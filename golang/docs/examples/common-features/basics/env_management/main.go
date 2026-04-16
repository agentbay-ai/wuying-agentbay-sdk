// Example: session-scoped environment variables via the Env module.
//
// Demonstrates set, get (all and by keys), overwrite, and shell visibility.
package main

import (
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

const imageID = "AIO_ubuntu2404"

func main() {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		log.Fatal("AGENTBAY_API_KEY environment variable is not set")
	}

	ab, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		log.Fatalf("NewAgentBay: %v", err)
	}

	fmt.Println("Creating session...")
	createResult, err := ab.Create(agentbay.NewCreateSessionParams().WithImageId(imageID))
	if err != nil {
		log.Fatalf("Create: %v", err)
	}
	if !createResult.Success || createResult.Session == nil {
		log.Fatalf("Create failed: %s", createResult.ErrorMessage)
	}
	session := createResult.Session
	fmt.Printf("Session ID: %s\n", session.SessionID)

	defer func() {
		fmt.Println("\nDeleting session...")
		if _, delErr := ab.Delete(session); delErr != nil {
			log.Printf("Delete: %v", delErr)
		} else {
			fmt.Println("Done.")
		}
	}()

	fmt.Println("\n1. Set environment variables")
	setResult, err := session.Env.Set(map[string]string{
		"DEMO_APP":   "agentbay",
		"DEMO_STAGE": "dev",
	})
	if err != nil {
		log.Fatalf("Env.Set: %v", err)
	}
	if !setResult.Success {
		log.Fatalf("Env.Set failed: %s", setResult.ErrorMessage)
	}
	fmt.Printf("set ok (requestId: %s)\n", setResult.RequestID)

	fmt.Println("\n2. Get all environment variables (subset printed)")
	allResult, err := session.Env.Get()
	if err != nil {
		log.Fatalf("Env.Get all: %v", err)
	}
	if !allResult.Success {
		log.Fatalf("Env.Get all failed: %s", allResult.ErrorMessage)
	}
	fmt.Printf("DEMO_APP=%s, DEMO_STAGE=%s\n", allResult.Envs["DEMO_APP"], allResult.Envs["DEMO_STAGE"])

	fmt.Println("\n3. Get specific keys only")
	keyResult, err := session.Env.Get("DEMO_APP")
	if err != nil {
		log.Fatalf("Env.Get keys: %v", err)
	}
	if !keyResult.Success {
		log.Fatalf("Env.Get keys failed: %s", keyResult.ErrorMessage)
	}
	fmt.Printf("DEMO_APP=%s\n", keyResult.Envs["DEMO_APP"])

	fmt.Println("\n4. Overwrite an existing variable")
	if _, err = session.Env.Set(map[string]string{"DEMO_STAGE": "prod"}); err != nil {
		log.Fatalf("Env.Set overwrite: %v", err)
	}
	after, err := session.Env.Get("DEMO_STAGE")
	if err != nil {
		log.Fatalf("Env.Get after overwrite: %v", err)
	}
	if after.Envs["DEMO_STAGE"] != "prod" {
		log.Fatalf("expected DEMO_STAGE=prod, got %q", after.Envs["DEMO_STAGE"])
	}
	fmt.Printf("DEMO_STAGE is now %s\n", after.Envs["DEMO_STAGE"])

	fmt.Println("\n5. Verify variables are visible to shell commands")
	cmdResult, err := session.Command.ExecuteCommand("echo $DEMO_APP", 5000)
	if err != nil {
		log.Fatalf("ExecuteCommand: %v", err)
	}
	if !cmdResult.Success {
		log.Fatalf("command failed: %s", cmdResult.ErrorMessage)
	}
	echoed := strings.TrimSpace(cmdResult.Stdout)
	if echoed != "agentbay" {
		log.Fatalf("expected shell to echo agentbay, got %q", echoed)
	}
	fmt.Printf("echo $DEMO_APP -> %q\n", echoed)
}
