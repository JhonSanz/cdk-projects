from constructs import Construct
from aws_cdk import (
    Stack,
    aws_codebuild as codebuild,
    aws_codepipeline as pipeline,
    aws_codecommit as codecommit,
    aws_codepipeline_actions as pipelineactions,
)


class PythonandfamilyWebsitePipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        build_image = codebuild.Project(
            self, "BuildImage",
            build_spec=codebuild.BuildSpec.from_source_filename(
                "buildspec.yaml"),
            source=codebuild.Source.git_hub(
                owner="<owner>",
                repo="<repo>"
            ),
            environment=codebuild.BuildEnvironment(
                privileged=True
            ),
            environment_variables={
                # "AWS_ACCOUNT_ID": codebuild.BuildEnvironmentVariable(value=os.getenv('CDK_DEFAULT_ACCOUNT') or ""),
                # "REGION": codebuild.BuildEnvironmentVariable(value=os.getenv('CDK_DEFAULT_REGION') or ""),
                # "IMAGE_TAG": codebuild.BuildEnvironmentVariable(value="latest"),
                # "IMAGE_REPO_NAME": codebuild.BuildEnvironmentVariable(value=image_repo.repository_name),
                # "REPOSITORY_URI": codebuild.BuildEnvironmentVariable(value=image_repo.repository_uri),
                # "TASK_DEFINITION_ARN": codebuild.BuildEnvironmentVariable(value=fargate_task_def.task_definition_arn),
                # "TASK_ROLE_ARN": codebuild.BuildEnvironmentVariable(value=fargate_task_def.task_role.role_arn),
                # "EXECUTION_ROLE_ARN": codebuild.BuildEnvironmentVariable(value=fargate_task_def.execution_role.role_arn)
            }
        )

        # Creates new pipeline artifacts
        source_code_artifact = pipeline.Artifact("SourceCodeArtifact")
        build_artifact = pipeline.Artifact("BuildArtifact")

        # Creates the source stage for CodePipeline
        source_stage = pipeline.StageProps(
            stage_name="Source",
            actions=[
                pipelineactions.GitHubSourceAction(
                    action_name="FetchSourceCode",
                    output=source_code_artifact,
                    owner="",
                    repo="",
                    branch="aws_master",
                    oauth_token=cdk.SecretValue.secrets_manager('my-github-token'),
                )
            ]
        )

        # Creates the build stage for CodePipeline
        build_stage = pipeline.StageProps(
            stage_name="Build",
            actions=[
                pipelineactions.CodeBuildAction(
                    action_name="DockerBuildPush",
                    input=pipeline.Artifact("SourceArtifact"),
                    project=build_image,
                    outputs=[build_artifact]
                )
            ]
        )

        # Creates a new CodeDeploy Deployment Group
        # deployment_group = codedeploy.EcsDeploymentGroup(
        #     self, "CodeDeployGroup",
        #     service=fargate_service,
        #     # Configurations for CodeDeploy Blue/Green deployments
        #     blue_green_deployment_config=codedeploy.EcsBlueGreenDeploymentConfig(
        #         listener=alb_listener,
        #         blue_target_group=target_group_blue,
        #         green_target_group=target_group_green
        #     )
        # )

        # Creates the deploy stage for CodePipeline
        # deploy_stage = pipeline.StageProps(
        #     stage_name="Deploy",
        #     actions=[
        #         pipelineactions.CodeDeployEcsDeployAction(
        #             action_name="EcsFargateDeploy",
        #             app_spec_template_input=build_artifact,
        #             task_definition_template_input=build_artifact,
        #             deployment_group=deployment_group
        #         )
        #     ]
        # )

        # Creates an AWS CodePipeline with source, build, and deploy stages
        pipeline.Pipeline(
            self, "BuildDeployPipeline",
            pipeline_name="ImageBuildDeployPipeline",
            stages=[source_stage, build_stage] #, deploy_stage]
        )