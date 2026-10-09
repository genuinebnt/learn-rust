//! Port of `src/execution/executor_factory.cpp`: the executor for a plan node. Given code. (The executors that the course's modules ask
//! you to write are created here too, once they exist.)

use super::executor_context::ExecutorContext;
use super::executors::abstract_executor::ExecutorBox;
use super::executors::aggregation_executor::AggregationExecutor;
use super::executors::delete_executor::DeleteExecutor;
use super::executors::hash_join_executor::HashJoinExecutor;
use super::executors::init_check_executor::InitCheckExecutor;
use super::executors::nested_index_join_executor::NestedIndexJoinExecutor;
use super::executors::nested_loop_join_executor::NestedLoopJoinExecutor;
use super::executors::filter_executor::FilterExecutor;
use super::executors::index_scan_executor::IndexScanExecutor;
use super::executors::insert_executor::InsertExecutor;
use super::executors::mock_scan_executor::MockScanExecutor;
use super::executors::projection_executor::ProjectionExecutor;
use super::executors::seq_scan_executor::SeqScanExecutor;
use super::executors::update_executor::UpdateExecutor;
use super::executors::values_executor::ValuesExecutor;
use super::check_options::CheckOption;
use super::plans::plan_node::{PlanRef, PlanType};
use crate::common::exception::{Exception, ExceptionType, Result};

pub fn create_executor<'e>(ctx: &'e ExecutorContext<'e>, plan: &PlanRef) -> Result<ExecutorBox<'e>> {
    match plan.plan_type() {
        PlanType::MockScan => Ok(Box::new(MockScanExecutor::new(plan.clone()))),
        PlanType::Projection => {
            let child = create_executor(ctx, &plan.children[0])?;
            Ok(Box::new(ProjectionExecutor::new(plan.clone(), child)))
        }
        PlanType::Filter => {
            let child = create_executor(ctx, &plan.children[0])?;
            Ok(Box::new(FilterExecutor::new(plan.clone(), child)))
        }
        PlanType::Values => Ok(Box::new(ValuesExecutor::new(plan.clone()))),
        PlanType::SeqScan => Ok(Box::new(SeqScanExecutor::new(ctx, plan.clone())?)),
        PlanType::IndexScan => Ok(Box::new(IndexScanExecutor::new(ctx, plan.clone())?)),
        PlanType::Insert => {
            let child = create_executor(ctx, &plan.children[0])?;
            Ok(Box::new(InsertExecutor::new(ctx, plan.clone(), child)?))
        }
        PlanType::Update => {
            let child = create_executor(ctx, &plan.children[0])?;
            Ok(Box::new(UpdateExecutor::new(ctx, plan.clone(), child)?))
        }
        PlanType::Aggregation => {
            let child = create_executor(ctx, &plan.children[0])?;
            Ok(Box::new(AggregationExecutor::new(plan.clone(), child)))
        }
        PlanType::NestedLoopJoin => {
            let (left_plan, right_plan) = (&plan.children[0], &plan.children[1]);
            let (left, right) = (create_executor(ctx, left_plan)?, create_executor(ctx, right_plan)?);
            if ctx.check_options().check_options_set.contains(&CheckOption::EnableNljCheck) {
                // count how often each side is initialised and asked for tuples
                let (left, right) = (InitCheckExecutor::new(left_plan.clone(), left), InitCheckExecutor::new(right_plan.clone(), right));
                ctx.add_check_executor(left.counters(), right.counters());
                return Ok(Box::new(NestedLoopJoinExecutor::new(plan.clone(), Box::new(left), Box::new(right))?));
            }
            Ok(Box::new(NestedLoopJoinExecutor::new(plan.clone(), left, right)?))
        }
        PlanType::HashJoin => {
            let (left, right) = (create_executor(ctx, &plan.children[0])?, create_executor(ctx, &plan.children[1])?);
            Ok(Box::new(HashJoinExecutor::new(plan.clone(), left, right)?))
        }
        PlanType::NestedIndexJoin => {
            let child = create_executor(ctx, &plan.children[0])?;
            Ok(Box::new(NestedIndexJoinExecutor::new(ctx, plan.clone(), child)?))
        }
        PlanType::Delete => {
            let child = create_executor(ctx, &plan.children[0])?;
            Ok(Box::new(DeleteExecutor::new(ctx, plan.clone(), child)?))
        }
        other => Err(Exception::new(ExceptionType::NotImplemented, format!("there is no executor for {other:?} plans (yet)"))),
    }
}
